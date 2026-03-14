# SROS v1 Evolution Plan

**Document:** Canonical plan for evolving SROS v1 toward full operational spec.  
**Last Updated:** 2025-11-24  
**Version:** 1.0

---

## Executive Summary

SROS v1 is **architecturally complete** but **operationally incomplete**. All 4 planes (Kernel, Runtime, Governance, MirrorOS) exist with clear separation of concerns. However, many implementations are **stubs or shallow**, and key workflows are missing. This plan prioritizes measurable, tested slices to progress from skeleton to functional OS.

**Current Status:** 36 tests passing (75%), 5 failing (fixable), 7 skipped (Gemini integration, needs API key).

---

## Current Plane Coverage

### Kernel Plane — **Partial (60%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `kernel_bootstrap.py` | ✅ Working | Starts heartbeat daemon, initializes config |
| `kernel_state.py` | ✅ Working | Thread-safe global state with session tracking |
| `kernel_config.py` | ✅ Working | YAML/env config loading |
| `event_bus.py` | ✅ Working | Pub/sub for inter-plane events |
| `daemon_registry.py` | ✅ Working | Catalog & lifecycle management |
| **Daemons (7 files)** | ❌ Stubs | `scheduler_daemon.py`, `adapter_daemon.py`, `telemetry_daemon.py`, `security_daemon.py`, `memory_daemon.py`, `resource_daemon.py`, `health_daemon.py` — placeholders only |

**Gap:** No real resource scheduling, health monitoring, or daemon orchestration.

---

### Runtime Plane — **Partial (55%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `session_manager.py` | ⚠️ Partial | Session create/resume; memory linkage incomplete |
| `context_builder.py` | ⚠️ Partial | Prompt composition from workflows; policy integration shallow |
| `workflow_engine.py` | ⚠️ Partial | Graph execution skeleton; missing `witness` arg in `__init__` (test fails) |
| **4 Agents** | ✅ Working | Architect, Builder, Tester, Base — functional with Gemini/OpenAI adapters |
| **Workflows/** | ❌ Empty | No `.srxml` workflow files; no examples |
| **Tools/** | ⚠️ Partial | 5+ tool adapters exist; routing is basic |
| **Simulations/** | ❌ Stub | Simulation harness not implemented |

**Gap:** No example workflows, no end-to-end orchestration demo, simulations incomplete.

---

### Governance Plane — **Partial (40%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `policy_engine.py` | ❌ Stub | Empty file; no YAML/SRXML policy parsing |
| `policy_enforcer.py` | ⚠️ Partial | Decorator-based enforcement; no real policies |
| `access_control.py` | ⚠️ Partial | RBAC skeleton; implementation thin |
| `audit_log.py` | ✅ Working | JSONL append-only log; records decisions |
| `cost_tracker.py` | ⚠️ Partial | Tracks model spend; no budget enforcement |

**Gap:** Policy parsing, real enforcement rules, secrets management, tenant isolation.

---

### MirrorOS Plane — **Partial (50%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `witness.py` | ✅ Working | Event log sink; routes to trace_store |
| `trace_store.py` | ✅ Working | JSONL trace persistence; query API |
| `telemetry_collector.py` | ⚠️ Partial | Aggregates metrics; limited dashboards |
| `drift_detector.py` | ⚠️ Partial | Anomaly detection skeleton; mostly stubs |
| `lenses.py` | ❌ Stub | Temporal/emotional/risk/identity lenses unimplemented |

**Gap:** Real lenses, replay engine, reflection engine, snapshot manager.

---

### Memory & Codex — **Partial (65%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `memory_router.py` | ✅ Working | Routes to backends; layer abstraction |
| **Backends/** | ✅ Working | SQLite, Vector, File backends functional |
| **Layers/** | ⚠️ Partial | Short-term, long-term, codex, analytics mapped; query API incomplete |
| `vector_store.py` | ✅ Working | ChromaDB integration for embeddings |
| `codex_index.py` | ⚠️ Partial | Indexes packs; packs are empty stubs |

**Gap:** Codex pack population (sros_core, sros_research, sros_playbooks), advanced query patterns.

---

### SRXML Core — **Partial (65%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `parser.py` | ⚠️ Partial | Parses XML→dict→object; missing fixture files (4 test failures) |
| `validator.py` | ✅ Working | Validates SRXML documents; all validation tests pass |
| **Schemas/** | ✅ Working | Core, agent_prompt, workflow, policy schemas exist |
| **Templates/** | ⚠️ Partial | Jinja2 templates for code generation; incomplete |

**Gap:** Example SRXML files, end-to-end template system, fixture files for tests.

---

### Adapters — **Partial (70%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `registry.py` | ✅ Working | Adapter discovery & caching |
| **Models/** | ✅ Working | Gemini, OpenAI, LocalLLM adapters; tests passing |
| **Tools/** | ⚠️ Partial | 5+ tool adapters; routing basic |
| **Storage/** | ⚠️ Partial | File, SQLite, Vector backends; incomplete |

**Gap:** Tool composition, advanced streaming, multi-modal support.

---

### Nexus (Control Surface) — **Partial (50%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `nexus_core.py` | ⚠️ Partial | Stub; 1 test failing (missing `witness` in WorkflowEngine) |
| **API/** | ⚠️ Partial | FastAPI server with 10+ endpoints; incomplete integration |
| **CLI/** | ⚠️ Partial | Typer CLI with 15+ commands; mostly wiring |

**Gap:** End-to-end demo, production API wiring, CLI integration testing.

---

### Evolution (Ouroboros) — **Partial (55%)**
| Component | Status | Notes |
|-----------|--------|-------|
| `observer.py` | ✅ Working | Observes runtime behavior; tests pass |
| `analyzer.py` | ✅ Working | Analyzes traces; tests pass |
| `proposer.py` | ⚠️ Partial | Stub; generates improvement proposals |
| `safeguards.py` | ✅ Working | Guards against destructive proposals; tests pass |

**Gap:** Real proposer logic, feedback loop integration.

---

## Test Baseline (2025-11-24)

```
Results: 36 passed (75%), 5 failed (10%), 7 skipped (15%)

Passing Suites:
  - test_adapter_registry.py ................... 8/8 ✅
  - test_kernel_boot.py ...................... 1/1 ✅
  - test_model_adapters.py .................. 12/12 ✅
  - test_ouroboros.py ....................... 8/8 ✅
  - test_srxml_validator.py ................. 6/6 ✅

Failing Suites:
  - test_nexus_core.py ....................... 0/1 (WorkflowEngine missing witness)
  - test_srxml_parser.py ................... 2/6 (missing fixture files)

Skipped (Gemini integration, no API key):
  - test_agent_gemini.py ..................... 5/5 ⏭️
  - test_gemini_integration.py ............... 2/2 ⏭️
```

---

## Priority Gaps Ranked by Impact × Feasibility

### Tier 1: Quick Wins (High Impact, Low Effort) — **Do First**

**Gap 1.1: Fix SRXML Fixture Files**
- **Impact:** 4 parser tests failing; blocks SRXML workflow testing
- **Effort:** 1 hour (create sample_workflow.srxml, sample_agent_prompt.srxml)
- **Next Slice:** "SRXML Examples & Fixtures"

**Gap 1.2: Fix WorkflowEngine Missing `witness` Argument**
- **Impact:** Nexus demo broken; blocks end-to-end test
- **Effort:** 1 hour (update WorkflowEngine.__init__, verify MirrorOS integration)
- **Next Slice:** "Harden Nexus Core & Runtime Orchestration"

**Gap 1.3: Populate Codex Packs**
- **Impact:** Memory layer functional but codex empty; blocks knowledge access
- **Effort:** 2 hours (create 3 sample packs with Markdown entries)
- **Next Slice:** "Codex Pack Initialization & Query API"

### Tier 2: Foundational (Medium Impact, Medium Effort) — **Do Next**

**Gap 2.1: Harden Kernel Daemons**
- **Impact:** Daemons are stubs; no real resource mgmt, health monitoring, scheduling
- **Effort:** 4–6 hours (implement 2–3 key daemons with tests)
- **Examples:** `scheduler_daemon`, `health_daemon`, `telemetry_daemon`
- **Next Slice:** "Kernel Daemon Hardening: Scheduler & Health"

**Gap 2.2: Implement Policy Engine**
- **Impact:** Governance plane is 40% complete; policies not enforced
- **Effort:** 4–6 hours (YAML policy parsing, rule evaluation, tenant isolation)
- **Next Slice:** "Policy Engine: Parsing & Evaluation"

**Gap 2.3: Wire Workflow Orchestration End-to-End**
- **Impact:** Runtime workflows incomplete; no demo runs end-to-end
- **Effort:** 3–5 hours (complete workflow_engine, session linkage, demo)
- **Next Slice:** "Runtime Workflow Orchestration & Demo"

### Tier 3: Advanced (Medium Impact, High Effort) — **Plan for Later**

**Gap 3.1: Implement MirrorOS Lenses**
- **Impact:** Reflection/introspection incomplete; lenses are stubs
- **Effort:** 6–8 hours (temporal, emotional, risk, identity lenses)
- **Next Slice:** "MirrorOS Lenses & Reflection Engine"

**Gap 3.2: Complete Replay & Simulation**
- **Impact:** Debugging, simulation, and regression testing blocked
- **Effort:** 6–8 hours (replay_engine, simulation harness, scenarios)
- **Next Slice:** "MirrorOS Replay & Simulation"

**Gap 3.3: Production Nexus & Integration**
- **Impact:** API and CLI incomplete; no production wiring
- **Effort:** 8–10 hours (full API, CLI, authentication, deployment)
- **Next Slice:** "Nexus Production Hardening"

---

## Recommended Evolution Sequence

### Pass 1: **Baseline Infrastructure & Quick Wins** *(THIS PASS)*
1. ✅ Fix environment setup (done)
2. ✅ Run baseline tests (done)
3. ✅ Create EVOLUTION_PLAN.md & EVOLUTION_LOG.md (in progress)
4. 🔄 Scope next passes based on gaps
5. 🔄 Hand off to next agent with clear priorities

### Pass 2: **SRXML Examples & Fixtures + Nexus MirrorOS Wiring**
**Status:** Tier 1 quick wins — ~2 hours  
**Scope:**
- Fix test fixture path bug in `test_srxml_parser.py` (`.parent.parent` → `.parent`)
- Ensure `tests/fixtures/sample_workflow.srxml` and `sample_agent_prompt.srxml` are used correctly
- Wire `TraceStore` → `Witness` → `KernelContext` in `kernel_bootstrap.py`
- Update `NexusCore.run_command()` to pass witness to `WorkflowEngine`
- Add integration test for Nexus demo command
**Expected Result:** 42/48 tests passing (88%), demo runnable  
**Files to Modify:**
- `tests/test_srxml_parser.py` — Fix fixture path
- `sros/kernel/kernel_bootstrap.py` — Wire witness
- `sros/apps/sros_web_nexus/nexus_core.py` — Pass witness to WorkflowEngine
- `sros/runtime/workflow_engine.py` — May need minor tweaks

### Pass 3: **Runtime Workflow Orchestration & Demo**
**Status:** Tier 2 foundational — ~4–5 hours  
**Scope:**
- Create sample workflow SRXML files in `sros/runtime/workflows/`
- Complete `SessionManager` → `MemoryRouter` linking (session_id → memory context)
- Enhance `ContextBuilder` to pull from codex and policies
- Build end-to-end SROS demo script:
  1. Boot kernel
  2. Create session
  3. Run workflow with agents
  4. Access memory
  5. Verify MirrorOS traces
- Add 5+ tests for workflow execution
**Expected Result:** Full demo passes with E2E logging, Runtime plane at 70%+  
**Files to Modify:**
- `sros/runtime/session_manager.py` — Link to memory_router
- `sros/runtime/context_builder.py` — Wire codex + policies
- `sros/runtime/workflow_engine.py` — Complete step execution
- `scripts/` — Add demo script (or enhance existing)

### Pass 4: **Kernel Daemon Hardening** (Optional, depends on priorities)
**Status:** Tier 2 foundational — ~4–6 hours  
**Scope:**
- Implement `SchedulerDaemon` (task queue, priority scheduling)
- Implement `HealthDaemon` (heartbeat monitoring, resource checks)
- Wire into bootstrap and add lifecycle tests
- Add metrics/dashboard hooks
**Expected Result:** Kernel plane at 80%+, 10+ new daemon tests  
**Files to Create:**
- `sros/kernel/daemons/scheduler_daemon.py`
- `sros/kernel/daemons/health_daemon.py`
- Tests for both

### Pass 5: **Policy Engine Implementation** (Optional, depends on priorities)
**Status:** Tier 2 foundational — ~4–6 hours  
**Scope:**
- Implement YAML/SRXML policy parsing in `policy_engine.py`
- Add rule evaluation engine (conditions, actions, effects)
- Integrate with `policy_enforcer.py` for enforcement
- Add tenant isolation and secrets management stubs
**Expected Result:** Governance plane at 70%+, policy enforcement working  
**Files to Modify:**
- `sros/governance/policy_engine.py` — Full implementation
- `sros/governance/access_control.py` — Tenant isolation
- `sros/governance/` — Tests

### Pass 6+: **Advanced Slices** (Lenses, Replay, Production Nexus)

---

## Success Criteria for This Pass

- ✅ EVOLUTION_PLAN.md created with plane status and ranked gaps
- ✅ EVOLUTION_LOG.md created with baseline entry and trace
- ✅ Test baseline documented (36 passed, 5 failed, 7 skipped)
- ✅ Clear next 2–3 slices identified with scope and effort estimates
- ✅ Repo left in resumable state for next agent

---

## Detailed Audit Findings & Pass 2 Specifics

### Bug 1: SRXML Parser Fixture Path

**Location:** `tests/test_srxml_parser.py`, line 18  
**Issue:** `Path(__file__).parent.parent / "fixtures"` resolves to `sros_v1/fixtures/`, but files are in `tests/fixtures/`  
**Symptom:** 4 parser tests fail with `FileNotFoundError`  
**Fix:** Change `.parent.parent` to `.parent`  
**Effort:** 1 line change

### Bug 2: WorkflowEngine `witness` Missing in NexusCore

**Location:** `sros/apps/sros_web_nexus/nexus_core.py`, line 20  
**Issue:** `WorkflowEngine(self.kernel)` passes only kernel, but needs `witness` parameter  
**Root Cause:** MirrorOS plane not wired into KernelContext  
**Symptom:** `test_nexus_core.py` fails with `TypeError: WorkflowEngine.__init__() missing 1 required positional argument: 'witness'`  
**Fix:** 
1. In `kernel_bootstrap.py`, add MirrorOS wiring to KernelContext (create TraceStore, Witness, expose via KernelContext)
2. In `nexus_core.py`, pass witness: `WorkflowEngine(self.kernel.event_bus, self.kernel.witness)`  
**Effort:** 3–4 line changes + new wiring logic (~30 lines total)

### Bug 3: Dataclass Field Ordering (FIXED in Pass 1)

**Location:** `sros/srxml/models/agent.py`, `workflow.py`  
**Issue:** Non-default fields after default inherited fields  
**Fix Applied:** Added sensible defaults to `role` and `mode`  
**Status:** ✅ Fixed

### Integration Gap 1: SessionManager → MemoryRouter Not Linked

**Location:** `sros/runtime/session_manager.py`, `context_builder.py`  
**Issue:** Sessions created but `memory_context` not linked to actual MemoryRouter  
**Impact:** Memory operations in workflows incomplete  
**Fix Needed:** Wire `kernel.memory.set_context(session_id, ...)` in session manager  
**Effort:** 5–10 lines

### Integration Gap 2: ContextBuilder → Codex Incomplete

**Location:** `sros/runtime/context_builder.py`  
**Issue:** Codex search commented out; policies not pulled  
**Impact:** Agent context missing knowledge and policy guidance  
**Fix Needed:** Uncomment/implement codex search, add policy lookup  
**Effort:** 10–15 lines

### Missing Fixtures (Not Actually Missing)

**Location:** `tests/fixtures/`  
**Status:** ✅ Files exist:
- `sample_workflow.srxml`
- `sample_agent_prompt.srxml`
- `codex_seed.json`
- `memory_seed.json`
- `policies/` (directory)

**Why Tests Fail:** Path bug (Bug 1), not missing files.

---

## Notes for Next Agent

1. **Environment Setup:** Python 3.13, SROS package installed in editable mode, all imports working.
2. **Test Status:** 36/48 passing. With Bug 1 + Bug 2 fixes, expect 42/48 (88%).
3. **Next Steps:** Start with Pass 2 bugs (1 hour each), then move to Pass 3 integration work.
4. **Docs:** Refer to Knowledge/SROS_v1_Blueprint.md for architectural intent; use Master_SROS_Schemas for schema guidance.
5. **Non-Regression:** All changes must pass tests and be logged in EVOLUTION_LOG.md with clear rationale.
6. **Resumption:** When you restart, check EVOLUTION_LOG.md for prior work and update EVOLUTION_PLAN.md accordingly.

---

**Next Action:** See EVOLUTION_LOG.md for this pass's detailed work log and proceed to Pass 2.
