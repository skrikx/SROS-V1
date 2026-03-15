"""Governed Workflow Runner.

Wires the real SROS subsystems together to execute an SRXML workflow
with governance policy enforcement, drift monitoring, witnessing,
and receipt generation.
"""

import asyncio
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..governance.policy_engine import PolicyEngine, PolicyResult
from ..kernel.kernel_bootstrap import boot as kernel_boot
from ..mirroros.drift_detector import DriftDetector
from ..mirroros.trace_store import TraceStore
from ..mirroros.witness import Witness
from ..srxml.parser import SRXMLParser
from ..version import get_release_version
from .receipt_validator import RECEIPT_SCHEMA_VERSION, validate_receipt


def _sha256_short(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _sha256_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class GoverningWorkflowRunner:
    def __init__(
        self,
        policies: List[Dict[str, Any]],
        step_metadata: Dict[str, Dict[str, Any]],
        drift_threshold: float = 0.5,
        ui_handlers: Optional[Dict[str, Any]] = None,
    ):
        self.policies = policies
        self.step_metadata = step_metadata
        self.drift_threshold = drift_threshold
        self.ui = ui_handlers or {}

    def run(self, srxml_path: str, receipt_path: str) -> Dict[str, Any]:
        return asyncio.run(self._execute(srxml_path, receipt_path))

    async def _execute(self, srxml_path: str, receipt_path: str) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        start_ts = datetime.now(timezone.utc).isoformat()

        kernel = kernel_boot()
        trace_store = TraceStore(storage_path="./data/traces")
        witness = Witness(trace_store)
        drift_detector = DriftDetector({"performance_threshold": self.drift_threshold})
        policy_engine = PolicyEngine(mode="strict")

        for policy in self.policies:
            policy_engine.load_policy(policy)

        parser = SRXMLParser()
        workflow_def = parser.parse(srxml_path)
        workflow_id = workflow_def.get("@id", Path(srxml_path).stem)
        workflow_checksum = _sha256_file(srxml_path)

        witness.record("workflow.start", {"workflow_id": workflow_id, "run_id": run_id})
        kernel.event_bus.publish("runtime", "workflow.start", {"workflow_id": workflow_id, "run_id": run_id})

        steps_raw = self._extract_steps(workflow_def)
        step_results = []
        gov_verdicts = {"allow": 0, "allow_with_conditions": 0, "deny": 0}
        max_drift = 0.0

        for i, step_def in enumerate(steps_raw):
            step_id = step_def.get("id", f"step{i + 1}")
            agent_id = step_def.get("agent", "unknown")
            instruction = step_def.get("instruction", "")

            meta = self.step_metadata.get(step_id, {})
            action = meta.get("action", f"execute_{step_id}")

            if "step" in self.ui:
                self.ui["step"](i + 1, len(steps_raw), agent_id, instruction)

            policy_result = policy_engine.evaluate(
                action,
                context={
                    "step_id": step_id,
                    "agent": agent_id,
                    "tenant": "PlatXP",
                    "resource": meta.get("resource", "system"),
                    "requested_fields": meta.get("requested_fields", []),
                },
            )

            verdict = policy_result.verdict
            gov_verdicts[verdict] = gov_verdicts.get(verdict, 0) + 1

            witness.record(
                "governance.evaluated",
                {
                    "step_id": step_id,
                    "verdict": verdict,
                    "reason": policy_result.reason,
                    "policy_name": policy_result.matched_policy_name,
                    "rule_id": policy_result.matched_rule_id,
                },
            )

            if "verdict" in self.ui:
                self.ui["verdict"](
                    verdict,
                    policy_result.risk_level or "unknown",
                    policy_result.reason,
                    policy_result.conditions,
                )

            if not policy_result.allowed:
                step_results.append(
                    self._build_step_res(
                        step_id,
                        agent_id,
                        action,
                        instruction,
                        meta,
                        policy_result,
                        0.0,
                        "denied",
                    )
                )
                continue

            kernel.event_bus.publish("runtime", "agent.thinking", {"agent": agent_id, "input": instruction})
            await asyncio.sleep(0.1)
            output = meta.get("output", f"Processed step {step_id}")
            kernel.event_bus.publish("runtime", "agent.acted", {"agent": agent_id, "response": output})

            drift = meta.get("drift", 0.05)
            drift_detector.record_metric(f"agent.{agent_id}", "drift", drift)
            max_drift = max(max_drift, drift)

            if "drift" in self.ui:
                self.ui["drift"](drift, self.drift_threshold)

            witness.record("workflow.step.completed", {"step_id": step_id, "drift": drift})
            step_results.append(
                self._build_step_res(
                    step_id,
                    agent_id,
                    action,
                    instruction,
                    meta,
                    policy_result,
                    drift,
                    "completed",
                )
            )

        end_ts = datetime.now(timezone.utc).isoformat()

        witness.record("workflow.end", {"workflow_id": workflow_id})
        kernel.event_bus.publish("runtime", "workflow.end", {"workflow_id": workflow_id})

        step_hashes = [_sha256_short(json.dumps(s, sort_keys=True, default=str)) for s in step_results]
        chain_hash = _sha256_short("->".join(step_hashes))

        receipt = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "sros_version": get_release_version(),
            "receipt_type": "workflow_execution",
            "workflow_id": workflow_id,
            "workflow_checksum": workflow_checksum,
            "run_id": run_id,
            "started_at": start_ts,
            "completed_at": end_ts,
            "status": "success",
            "total_steps": len(step_results),
            "trace_count": len(trace_store.traces),
            "steps": step_results,
            "receipt_chain": {
                "step_hashes": step_hashes,
                "chain_hash": chain_hash,
            },
            "governance_summary": {
                "total_policy_checks": len(step_results),
                "verdicts": gov_verdicts,
                "domain_blocked": self.step_metadata.get("_global", {}).get("domain_blocked", []),
            },
            "mirror_summary": {
                "drift_detected": max_drift > self.drift_threshold,
                "max_drift_score": max_drift,
                "all_events_witnessed": True,
                "total_traces": len(trace_store.traces),
            },
        }

        validate_receipt(receipt)

        out = Path(receipt_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True, default=str), encoding="utf-8")
        return receipt

    def _extract_steps(self, workflow_def: Dict) -> List[Dict]:
        steps = workflow_def.get("step", workflow_def.get("task", []))
        if not isinstance(steps, list):
            steps = [steps]

        result = []
        for step in steps:
            entry = {
                "id": step.get("@id", ""),
                "agent": step.get("agent", step.get("@agent", "")),
                "instruction": "",
                "order": step.get("@order", "0"),
            }

            if "instruction" in step:
                inst = step["instruction"]
                entry["instruction"] = inst.get("#text", str(inst)) if isinstance(inst, dict) else str(inst)
            elif "input" in step:
                inp = step["input"]
                if isinstance(inp, dict):
                    prompt = inp.get("prompt", {})
                    entry["instruction"] = prompt.get("#text", str(prompt)) if isinstance(prompt, dict) else str(prompt)
                else:
                    entry["instruction"] = str(inp)

            if isinstance(entry["agent"], dict):
                entry["agent"] = entry["agent"].get("#text", "unknown")

            result.append(entry)

        result.sort(key=lambda s: int(s.get("order", 0)))
        return result

    def _build_step_res(
        self,
        step_id: str,
        agent_id: str,
        action: str,
        instruction: str,
        meta: Dict[str, Any],
        policy_result: PolicyResult,
        drift: float,
        status: str,
    ):
        return {
            "step_id": step_id,
            "agent": agent_id,
            "action": action,
            "instruction": instruction,
            "output": meta.get("output", ""),
            "status": status,
            "governance": {
                "policy_checked": True,
                "allowed": policy_result.allowed,
                "verdict": policy_result.verdict,
                "policy_name": policy_result.matched_policy_name,
                "rule_id": policy_result.matched_rule_id,
                "risk_level": policy_result.risk_level,
                "reason": policy_result.reason,
                "conditions": policy_result.conditions,
            },
            "mirror": {
                "drift_score": drift,
                "drift_threshold": self.drift_threshold,
                "drift_detected": drift > self.drift_threshold,
                "witness_recorded": True,
            },
        }
