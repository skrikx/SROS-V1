# SROS Planes Reference

> Detailed documentation for each SROS plane and its modules.

---

## Overview

SROS is organized into four logical planes:

| Plane | Directory | Files | Purpose |
|-------|-----------|-------|---------|
| Kernel | `sros/kernel/` | 6 | System foundation |
| Runtime | `sros/runtime/` | 21 | Agent execution |
| Governance | `sros/governance/` | 8 | Policy enforcement |
| MirrorOS | `sros/mirroros/` | 6 | Observability |

---

## Plane 1: Kernel

**Location**: `sros/kernel/`

The Kernel plane is the stable backbone of SROS. Everything else is a client of the kernel.

### Module Reference

| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | - | Package exports |
| `kernel_bootstrap.py` | ~50 | Boots SROS, loads config, initializes subsystems |
| `kernel_state.py` | ~80 | Central state object for the OS |
| `kernel_config.py` | ~60 | Configuration loading and management |
| `event_bus.py` | ~70 | Inter-plane event communication |
| `daemon_registry.py` | ~60 | Daemon lifecycle management |

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `daemons/` | Background daemons (heartbeat, etc.) |
| `adapters/` | Low-level adapter interfaces |

### Key Classes

```python
# kernel_bootstrap.py
class KernelBootstrap:
    def boot(config_path: str = "sros_config.yml") -> KernelState
    def shutdown() -> None

# kernel_state.py
class KernelState:
    status: str  # "booting", "running", "shutdown"
    registered_agents: List[str]
    active_sessions: Dict[str, Session]

# event_bus.py
class EventBus:
    def subscribe(topic: str, handler: Callable) -> None
    def publish(topic: str, data: dict) -> None
```

### Events Published

| Event | When | Data |
|-------|------|------|
| `kernel.boot` | Kernel starts | `{version, timestamp}` |
| `kernel.ready` | Boot complete | `{status}` |
| `kernel.heartbeat` | Periodic | `{uptime, health}` |
| `kernel.shutdown` | Shutdown | `{reason}` |

---

## Plane 2: Runtime

**Location**: `sros/runtime/`

The Runtime plane is where agents live, communicate, and perform tasks.

### Module Reference

| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | - | Package exports |
| `workflow_engine.py` | ~120 | Executes SRXML workflows |
| `session_manager.py` | ~70 | Session lifecycle |
| `context_builder.py` | ~50 | Builds agent context |

### Subdirectories

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `agents/` | 7 files | Agent implementations |
| `workflows/` | - | Runtime workflow storage |
| `tools/` | - | Agent tools |
| `simulations/` | 2 files | Sandboxed simulations |

### Agents

| Agent | File | Role |
|-------|------|------|
| `AgentBase` | `agent_base.py` | Base class for all agents |
| `ArchitectAgent` | `architect_agent.py` | System analysis and design |
| `BuilderAgent` | `builder_agent.py` | Code generation |
| `TesterAgent` | `tester_agent.py` | Test generation and QA |
| `SkrikxAgent` | `skrikx_agent.py` | Sovereign Prime interface |
| `SRXBaseAgent` | `srx_base_agent.py` | SRX agent base |

### Key Classes

```python
# workflow_engine.py
class WorkflowEngine:
    def run(workflow_path: str) -> WorkflowResult
    def validate(workflow_path: str) -> ValidationResult

# session_manager.py
class SessionManager:
    def create() -> str  # Returns session_id
    def get(session_id: str) -> Session
    def close(session_id: str) -> None

# agents/agent_base.py
class AgentBase:
    name: str
    role: str
    objective: str
    async def run(task: str, context: dict) -> str
```

---

## Plane 3: Governance

**Location**: `sros/governance/`

The Governance plane enforces rules, tracks costs, and maintains audit trails.

### Module Reference

| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | - | Package exports |
| `policy_engine.py` | ~60 | Policy evaluation |
| `policy_enforcer.py` | ~170 | Policy enforcement |
| `sovereign_directive.py` | ~220 | High-level directives |
| `access_control.py` | ~40 | Permission control |
| `cost_tracker.py` | ~230 | API cost tracking |
| `audit_log.py` | ~40 | Event logging |
| `sovereign_audit_log.py` | ~120 | Enhanced audit logging |

### Key Classes

```python
# policy_engine.py
class PolicyEngine:
    def evaluate(action: str, context: dict) -> PolicyDecision
    # Returns: "allow", "deny", or "modify"

# policy_enforcer.py
class PolicyEnforcer:
    def check(action: str, agent: str, context: dict) -> bool
    def enforce(action: str, context: dict) -> EnforcementResult

# cost_tracker.py
class CostTracker:
    def record_usage(adapter: str, tokens: int, cost: float) -> None
    def get_budget_status() -> BudgetStatus
    def is_budget_exceeded() -> bool

# sovereign_directive.py
class SovereignDirective:
    directive_type: str  # "execute", "observe", "restrict"
    target: str
    parameters: dict
```

### Policy Types

| Type | Purpose | Example |
|------|---------|---------|
| Safety | Block harmful actions | Dangerous prompt detection |
| Cost | Budget enforcement | Daily/monthly limits |
| Access | Permission control | Agent-to-resource access |
| Compliance | Regulatory | Data retention rules |

---

## Plane 4: MirrorOS

**Location**: `sros/mirroros/`

MirrorOS provides self-awareness, observability, and introspection capabilities.

### Module Reference

| Module | Lines | Purpose |
|--------|-------|---------|
| `__init__.py` | - | Package exports |
| `witness.py` | ~50 | Event observation |
| `lenses.py` | ~40 | View filters |
| `trace_store.py` | ~80 | Trace storage |
| `drift_detector.py` | ~230 | Behavioral drift detection |
| `telemetry_collector.py` | ~200 | Metrics collection |

### Key Classes

```python
# witness.py
class Witness:
    def observe(subject: str, event: str, context: dict) -> None
    def get_observations(subject: str) -> List[Observation]

# drift_detector.py
class DriftDetector:
    def check_semantic_drift(current: str, baseline: str) -> DriftScore
    def set_threshold(threshold: float) -> None
    def is_drifting() -> bool

# telemetry_collector.py
class TelemetryCollector:
    def record_latency(operation: str, duration: float) -> None
    def record_error(operation: str, error: str) -> None
    def get_metrics() -> Dict[str, Metric]

# lenses.py
AVAILABLE_LENSES = ["temporal", "identity", "emotional", "risk"]
def apply_lens(lens: str, data: List[Observation]) -> FilteredData
```

### Lenses

| Lens | Purpose | Use Case |
|------|---------|----------|
| `temporal` | Compare to past states | Behavioral regression |
| `identity` | Check alignment | Identity drift |
| `emotional` | Assess tone | Output quality |
| `risk` | Evaluate harm | Safety monitoring |

---

## Support Layers

### SRXML (`sros/srxml/`)

| Module | Purpose |
|--------|---------|
| `parser.py` | Parse SRXML files |
| `validator.py` | Validate against schemas |
| `models/` | Pydantic models |
| `schemas/` | XML schema files |
| `templates/` | Starting templates |

### Memory (`sros/memory/`)

| Module | Purpose |
|--------|---------|
| `memory_router.py` | Route to layers |
| `short_term_memory.py` | Session memory |
| `long_term_memory.py` | Persistent memory |
| `codex_memory.py` | Domain knowledge |
| `vector_store.py` | Semantic search |

### Adapters (`sros/adapters/`)

| Module | Purpose |
|--------|---------|
| `base.py` | Base adapter class |
| `registry.py` | Adapter discovery |
| `models/` | Model adapters |
| `tools/` | Tool adapters |
| `storage/` | Storage adapters |

### Evolution (`sros/evolution/`)

| Module | Purpose |
|--------|---------|
| `ouroboros.py` | Self-evolution engine |
| `analyzer.py` | Behavior analysis |
| `proposer.py` | Improvement proposals |
| `observer.py` | Execution observation |
| `safeguards.py` | Safety validation |

### Nexus (`sros/nexus/`)

| Module | Purpose |
|--------|---------|
| `cli/` | Command-line interface |
| `api/` | HTTP API server |
| `nexus_core.py` | Core orchestration |

---

## Cross-Plane Communication

All planes communicate through the Kernel's event bus:

```
Runtime → Kernel.EventBus → Governance
    ↓                           ↓
MirrorOS ← Kernel.EventBus ← Governance
```

### Standard Event Flow

1. **Agent Request**: Runtime publishes `agent.run`
2. **Policy Check**: Governance receives and evaluates
3. **Execution**: Runtime executes if allowed
4. **Witness**: MirrorOS observes the event
5. **Result**: Response flows back through bus

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture diagrams
- [SROS_STUDY_GUIDE_v1.md](SROS_STUDY_GUIDE_v1.md) - Learning guide
- [API_REFERENCE.md](API_REFERENCE.md) - HTTP API documentation
