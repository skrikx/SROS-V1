# SROS v1: Sovereign Recursive Operating System

[![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue.svg)](VERSION)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## The Problem

AI agents are shipping to production without governance. When an agent accesses customer data, proposes code changes, or makes decisions that affect regulated processes, there is no policy enforcement, no audit trail, and no way to replay what happened.

This is not a theoretical risk. It is the reason compliance teams block agent deployments, engineering teams cannot debug agent failures, and organizations cannot prove to auditors what their AI systems actually did.

## What SROS Does

SROS is a **governance and observability runtime for AI agent execution**. It sits between your agents and the systems they touch, enforcing policies, generating verifiable receipts, and monitoring behavioral drift - all without modifying your existing models or infrastructure.

- **Policy enforcement** before every agent action (allow, deny, or allow-with-conditions)
- **Receipts** - JSON artifacts capturing every step, every policy verdict, every drift score
- **Drift monitoring** - detects when agent behavior deviates from baselines
- **Model-agnostic** - works with Gemini, OpenAI, local models, or any LLM
- **Hash-chained audit trails** - tamper-evident execution records

---

## Quickstart (2 minutes)

```bash
git clone https://github.com/skrikx/SROS-V1.git
cd SROS-V1
pip install -e .
sros run-demo
```

**What happens:** SROS boots a kernel, runs a 3-step agent workflow with governance policy checks at each step, monitors for behavioral drift, and writes a verifiable receipt to disk.

**Expected output:**

```
============================================================
  SROS v1 - Governance Receipt Demo
============================================================

  Booting SROS Kernel...
  [OK] Kernel online

  [Step 1/3] ArchitectAgent: Analyzing requirements...
    Policy check: ALLOW (read-only, low risk)
    Drift score: 0.02 / 0.50 threshold - OK
  [OK] Step 1 complete

  [Step 2/3] BuilderAgent: Proposing code mutation...
    Policy check: ALLOW WITH CONDITIONS (medium risk)
      - Max 50-line diff enforced
      - Must pass test suite before merge
    Drift score: 0.15 / 0.50 threshold - OK
  [OK] Step 2 complete

  [Step 3/3] TesterAgent: Generating validation tests...
    Policy check: ALLOW (test generation, low risk)
    Drift score: 0.04 / 0.50 threshold - OK
  [OK] Step 3 complete

  Receipt written to: receipts/demo_receipt.json
  Chain hash: 2b5558bb442e9b40
```

**Inspect the receipt:** Open `receipts/demo_receipt.json` to see the full governance trail - every step, every policy verdict, every drift measurement, linked by hash chain.

---

## What SROS Produces

Every workflow execution generates a **receipt** - a structured JSON artifact that captures:

```json
{
  "workflow_id": "governance_demo",
  "status": "success",
  "governance_summary": {
    "total_policy_checks": 3,
    "verdicts": { "allow": 2, "allow_with_conditions": 1, "deny": 0 }
  },
  "mirror_summary": {
    "drift_detected": false,
    "max_drift_score": 0.15,
    "all_events_witnessed": true
  },
  "receipt_chain": {
    "chain_hash": "2b5558bb442e9b40"
  }
}
```

Browse sample receipts without cloning:
- [Demo receipt](receipts/demo_receipt.json)
- [Fintech loan review](receipts/fintech_loan_review_receipt.json) - PII field governance
- [Healthcare triage](receipts/healthcare_triage_receipt.json) - HIPAA-aligned access control
- [Contract review](receipts/contract_review_receipt.json) - data exfiltration prevention

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│  Plane 4: MirrorOS    (Observability)                     │
│  Witnesses, traces, drift detection, telemetry            │
├───────────────────────────────────────────────────────────┤
│  Plane 3: Governance  (Policy Enforcement)                │
│  Policies, cost tracking, access control, audit logs      │
├───────────────────────────────────────────────────────────┤
│  Plane 2: Runtime     (Agent Execution)                   │
│  Agents, workflows, sessions, context building            │
├───────────────────────────────────────────────────────────┤
│  Plane 1: Kernel      (System Foundation)                 │
│  Event bus, config, state, daemons                        │
└───────────────────────────────────────────────────────────┘
         SRXML │ Memory │ Adapters │ Evolution
```

Planes communicate exclusively through the Kernel's event bus. Governance is synchronous (blocks until policy decision). MirrorOS is asynchronous (never blocks execution).

---

## What You Can Do With It

| If you are a... | SROS helps you... |
|-----------------|-------------------|
| **CTO** | Prove to your board that agent execution is governed and auditable |
| **VP Engineering** | Debug agent workflows with deterministic replay and execution traces |
| **Compliance Lead** | Generate receipts that show exactly what agents accessed and what was blocked |
| **Platform Engineer** | Add governance to existing agent workflows without rewriting models |

---

## Industry Example Workflows

SROS ships with domain-specific workflow examples that demonstrate governance in regulated environments:

| Example | Domain | Governance Demonstrated |
|---------|--------|------------------------|
| [Loan Review](examples/fintech_loan_review.srxml) | Financial Services | PII field restriction, Fair Lending compliance |
| [Healthcare Triage](examples/healthcare_triage.srxml) | Healthcare | HIPAA-aligned PHI access control |
| [Contract Review](examples/contract_review.srxml) | Legal | Data exfiltration prevention, summary-only output |

Each workflow produces a receipt showing every policy decision. See the [sample receipts](receipts/) directory.

---

## Pilot Evaluation Path

If you are evaluating SROS for your organization:

1. **Today**: Clone, install, run `sros run-demo`, inspect the receipt
2. **This week**: Review the [industry examples](examples/) and [sample receipts](receipts/)
3. **Next step**: Read the [Pilot Guide](docs/PILOT_GUIDE.md) for a 2-week evaluation plan

---

## Documentation

| Document | Audience |
|----------|----------|
| [Pilot Guide](docs/PILOT_GUIDE.md) | Evaluators considering a pilot deployment |
| [User Guide](docs/USER_GUIDE.md) | Developers, operators, contributors |
| [Architecture](docs/ARCHITECTURE.md) | Engineers evaluating system design |
| [Study Guide](docs/SROS_STUDY_GUIDE_v1.md) | Developers learning the system |
| [Contributing](CONTRIBUTING.md) | Open-source contributors |

---

## Testing

```bash
pytest tests/ -v
# 45 passed, 7 skipped, 0 failures
```

---

## Project Structure

```
sros/                    # Main package
├── kernel/              # Plane 1: Event bus, config, daemons
├── runtime/             # Plane 2: Agents, workflows, sessions
├── governance/          # Plane 3: Policies, cost tracking, audit
├── mirroros/            # Plane 4: Witness, drift, telemetry
├── srxml/               # Declarative schema language
├── memory/              # Multi-tier memory (short, long, codex, vector)
├── adapters/            # Model adapters (Gemini, OpenAI, local)
└── evolution/           # Self-improvement engine (Ouroboros)
tests/                   # 45 unit + integration tests
examples/                # SRXML workflow examples
receipts/                # Sample governance receipts
```

---

## Alpha Status

SROS v1 is in Alpha. The core architecture, governance enforcement, receipt generation, and drift monitoring are functional and tested. Extended CLI commands, HTTP API, and full LLM-integrated workflow execution are scaffolded for future releases. See [Known Limitations](docs/USER_GUIDE.md#27-known-limitations-and-honest-current-status) for details.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
