# SROS Study Guide v1

> A comprehensive learning guide for developers working with the Sovereign Runtime Operating System.

---

## Table of Contents

1. [What SROS Is](#1-what-sros-is)
2. [The Four Planes](#2-the-four-planes)
3. [Getting Started](#3-getting-started)
4. [Your First Workflow](#4-your-first-workflow)
5. [Deep Dive: Kernel Plane](#5-deep-dive-kernel-plane)
6. [Deep Dive: Runtime Plane](#6-deep-dive-runtime-plane)
7. [Deep Dive: Governance Plane](#7-deep-dive-governance-plane)
8. [Deep Dive: MirrorOS Plane](#8-deep-dive-mirroros-plane)
9. [SRXML Authoring Guide](#9-srxml-authoring-guide)
10. [Memory System](#10-memory-system)
11. [Adapters and Models](#11-adapters-and-models)
12. [Evolution and Self-Improvement](#12-evolution-and-self-improvement)
13. [Extending SROS](#13-extending-sros)
14. [Troubleshooting](#14-troubleshooting)
15. [Next Steps](#15-next-steps)

---

## 1. What SROS Is

SROS (Sovereign Runtime Operating System) is an **AI operating system** designed to orchestrate complex agentic workflows. Unlike traditional applications that call AI models directly, SROS provides:

- **Structured Agent Environment**: Agents collaborate within defined boundaries
- **Strict Governance**: All actions are policy-checked before execution
- **Full Observability**: Every operation is witnessed and traced
- **Self-Evolution**: The system can analyze and improve itself

### Core Philosophy

```
┌─────────────────────────────────────────────────┐
│                 Your Application                 │
├─────────────────────────────────────────────────┤
│                      SROS                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Agents  │ │ Policies │ │ Memory   │        │
│  └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────┤
│              Model Adapters                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Gemini  │ │  OpenAI  │ │  Local   │        │
│  └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────┘
```

SROS **owns** governance, memory, and orchestration. Models are interchangeable adapters.

---

## 2. The Four Planes

SROS is organized into four logical planes, each with distinct responsibilities:

| Plane | Location | Purpose | Key Components |
|-------|----------|---------|----------------|
| **Kernel** | `sros/kernel/` | System foundation | Bootstrap, state, event bus |
| **Runtime** | `sros/runtime/` | Agent execution | Agents, workflows, sessions |
| **Governance** | `sros/governance/` | Policy enforcement | Policies, costs, audit |
| **MirrorOS** | `sros/mirroros/` | Observability | Witness, drift, telemetry |

### Plane Interaction Flow

```
User Request
     │
     ▼
┌─────────────┐     ┌─────────────┐
│   Runtime   │◄───►│  Governance │
│   (Agents)  │     │  (Policies) │
└──────┬──────┘     └─────────────┘
       │                   ▲
       ▼                   │
┌─────────────┐     ┌─────────────┐
│   Kernel    │◄───►│  MirrorOS   │
│  (Events)   │     │  (Witness)  │
└─────────────┘     └─────────────┘
```

---

## 3. Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (latest version)
- Optional: Gemini or OpenAI API key for external models

### Installation

```bash
# Navigate to the SROS directory
cd sros-v1-alpha

# Install in development mode
pip install -e .
```

### Initialize

```bash
sros init
```

This creates the default configuration and initializes the database.

### Verify Installation

```bash
sros status system
# Output: status: operational
```

### Run Demo

```bash
sros run-demo
```

This executes a complete demo workflow showcasing agents, memory, and telemetry.

---

## 4. Your First Workflow

### Running the Hello World Example

```bash
sros workflow run examples/hello_world_workflow.srxml
```

**Expected Output:**
```
Booting SROS Kernel (config=sros_config.yml)...
Starting Kernel Daemons...
  [OK] heartbeat
SROS Kernel Online.
[WorkflowEngine] Starting workflow: hello_world
  [STEP] task_1: What is the capital of France?
[WorkflowEngine] Workflow hello_world completed.
status: success
```

### Understanding the Workflow

The `hello_world_workflow.srxml` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<workflow name="hello_world" version="1.0">
    <metadata>
        <description>A simple hello world workflow</description>
    </metadata>
    
    <steps>
        <step id="task_1" agent="architect">
            <task>What is the capital of France?</task>
        </step>
    </steps>
</workflow>
```

**What happens:**
1. SROS boots the kernel
2. Workflow engine parses the SRXML
3. Step `task_1` is routed to the `architect` agent
4. Agent processes the task
5. MirrorOS witnesses the execution
6. Results are returned

---

## 5. Deep Dive: Kernel Plane

The Kernel plane (`sros/kernel/`) is the foundation of SROS.

### Key Components

| Module | Purpose |
|--------|---------|
| `kernel_bootstrap.py` | Boots SROS, loads config, initializes subsystems |
| `kernel_state.py` | Central state object for the OS |
| `kernel_config.py` | Configuration management |
| `event_bus.py` | Inter-plane communication |
| `daemon_registry.py` | Daemon lifecycle management |

### Event Bus

All planes communicate through the event bus:

```python
from sros.kernel.event_bus import EventBus

bus = EventBus()

# Subscribe to events
bus.subscribe("agent.run", handler_function)

# Publish events
bus.publish("agent.run", {"agent": "architect", "task": "..."})
```

### Kernel Boot Sequence

1. Load `sros_config.yml`
2. Initialize kernel state
3. Start event bus
4. Register and start daemons
5. Signal `kernel.ready`

---

## 6. Deep Dive: Runtime Plane

The Runtime plane (`sros/runtime/`) is where agents live and work.

### Agents

Agents are the "workers" of SROS. Each agent has:

- **Identity**: Name, role, purpose
- **Capabilities**: What it can do
- **Model Reference**: Which AI model it uses
- **Memory Access**: What memory layers it can access

#### Built-in Agents

| Agent | Role | Use Case |
|-------|------|----------|
| `architect` | System Architect | Analysis, design, root-cause |
| `builder` | Code Builder | Code generation, implementation |
| `tester` | Test Engineer | Test generation, QA |

#### Agent Lifecycle

```
1. Instantiation → Agent created from config
2. Context Building → Session context prepared
3. Model Call → AI model invoked via adapter
4. Response Processing → Output parsed and validated
5. Memory Write → Results stored if needed
6. Witness → MirrorOS logs the event
```

### Workflow Engine

The workflow engine (`workflow_engine.py`) executes SRXML workflows:

```python
from sros.runtime.workflow_engine import WorkflowEngine

engine = WorkflowEngine()
result = engine.run("path/to/workflow.srxml")
```

### Sessions

Sessions track agent interactions:

```python
from sros.runtime.session_manager import SessionManager

session = SessionManager()
session_id = session.create()
# ... agent work happens ...
session.close(session_id)
```

---

## 7. Deep Dive: Governance Plane

The Governance plane (`sros/governance/`) enforces rules and tracks compliance.

### Policy Engine

Policies define what agents can and cannot do:

```python
from sros.governance.policy_engine import PolicyEngine

engine = PolicyEngine()
decision = engine.evaluate(action="write_memory", context={...})
# Returns: allow, deny, or modify
```

### Policy Types

| Type | Purpose | Example |
|------|---------|---------|
| **Safety** | Prevent harmful actions | Block dangerous prompts |
| **Cost** | Budget enforcement | Daily API cost limits |
| **Access** | Permission control | Agent-to-memory access |
| **Compliance** | Regulatory rules | Data retention policies |

### Cost Tracking

```python
from sros.governance.cost_tracker import CostTracker

tracker = CostTracker()
tracker.record_usage("gemini", tokens=1000, cost=0.01)
status = tracker.get_budget_status()
# Returns: daily/monthly usage and limits
```

### Audit Log

All governance decisions are logged:

```python
from sros.governance.audit_log import AuditLog

log = AuditLog()
log.record("policy_check", {"action": "...", "decision": "allow"})
```

---

## 8. Deep Dive: MirrorOS Plane

MirrorOS (`sros/mirroros/`) provides self-awareness and observability.

### Witness

Every significant event passes through Witness:

```python
from sros.mirroros.witness import Witness

witness = Witness()
witness.observe(
    subject="architect_agent",
    event="task_completion",
    context={"task": "...", "result": "..."}
)
```

### Drift Detection

Drift detector watches for behavioral anomalies:

```python
from sros.mirroros.drift_detector import DriftDetector

detector = DriftDetector()
detector.check_semantic_drift(current_output, baseline)
# Returns: drift score and alert if threshold exceeded
```

### Lenses

Lenses provide different views of witness data:

| Lens | Purpose |
|------|---------|
| `temporal` | Compare to past behavior |
| `identity` | Check alignment with identity |
| `emotional` | Assess emotional state of outputs |
| `risk` | Evaluate risk and harm vectors |

### Telemetry

```python
from sros.mirroros.telemetry_collector import TelemetryCollector

telemetry = TelemetryCollector()
telemetry.record_latency("agent.run", 1.5)
metrics = telemetry.get_metrics()
```

---

## 9. SRXML Authoring Guide

SRXML is the XML-based language for defining workflows, agents, and policies.

### Workflow Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<workflow name="my_workflow" version="1.0">
    <metadata>
        <author>Your Name</author>
        <description>What this workflow does</description>
    </metadata>
    
    <steps>
        <!-- Sequential execution -->
        <step id="step_1" agent="architect">
            <task>Analyze the problem</task>
        </step>
        
        <!-- Dependent step -->
        <step id="step_2" agent="builder" depends_on="step_1">
            <task>Implement the solution</task>
        </step>
    </steps>
</workflow>
```

### Agent Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<agent name="custom_agent" version="1.0">
    <identity>
        <role>Custom Role</role>
        <objective>What this agent does</objective>
    </identity>
    
    <capabilities>
        <capability>code_generation</capability>
        <capability>analysis</capability>
    </capabilities>
    
    <model_ref>gemini</model_ref>
    
    <memory>
        <layer>short</layer>
        <layer>long</layer>
    </memory>
</agent>
```

### Policy Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<policy name="cost_limit" version="1.0">
    <rules>
        <rule id="daily_budget">
            <condition>daily_cost > 100.0</condition>
            <action>deny</action>
            <message>Daily budget exceeded</message>
        </rule>
    </rules>
</policy>
```

### Validating SRXML

```bash
# Validate before running
sros workflow validate path/to/workflow.srxml
```

---

## 10. Memory System

SROS provides a multi-layer memory system.

### Memory Layers

| Layer | Scope | Persistence | Use Case |
|-------|-------|-------------|----------|
| **Short-term** | Session | Session lifetime | Working memory |
| **Long-term** | Cross-session | Permanent | Persistent knowledge |
| **Codex** | System-wide | Permanent | Domain knowledge |
| **Vector** | Semantic | Permanent | Similarity search |

### Using Memory via CLI

```bash
# Write to short-term
sros memory write "Session note" --layer short

# Write to long-term with key
sros memory write "Persistent data" --layer long --key "my_key"

# Read from memory
sros memory read --layer long --query "search term"

# Get statistics
sros memory stats
```

### Using Memory in Code

```python
from sros.memory.memory_router import MemoryRouter

router = MemoryRouter()

# Write
router.write("short", "key", "value")

# Read
data = router.read("long", "key")

# Search
results = router.search("vector", "semantic query")
```

---

## 11. Adapters and Models

Adapters allow SROS to work with different AI models.

### Available Adapters

| Adapter | Provider | Configuration |
|---------|----------|---------------|
| `gemini` | Google | `GEMINI_API_KEY` |
| `openai` | OpenAI | `OPENAI_API_KEY` |
| `local` | Ollama/Local | `SROS_LOCAL_MODEL_URL` |

### Configuring Adapters

In `sros_config.yml`:

```yaml
adapters:
  default_model: "gemini"
  
  gemini:
    model: "gemini-pro"
    temperature: 0.7
    
  openai:
    model: "gpt-4"
    temperature: 0.7
```

### Using Adapters

```python
from sros.adapters.registry import AdapterRegistry

registry = AdapterRegistry()
adapter = registry.get("gemini")
response = await adapter.generate("Your prompt here")
```

---

## 12. Evolution and Self-Improvement

SROS can analyze and improve itself through the Ouroboros engine.

### Evolution Cycle

```
1. Observe → Collect behavioral data
2. Analyze → Identify patterns and issues
3. Propose → Generate improvement proposals
4. Validate → Check proposals against safeguards
5. Apply → Implement approved changes
```

### Safeguards

All self-modifications pass through safeguards:

```python
from sros.evolution.safeguards import Safeguards

safeguards = Safeguards()
is_safe = safeguards.validate_proposal(proposal)
```

### Manual Evolution

```python
from sros.evolution.ouroboros import Ouroboros

ouroboros = Ouroboros()
proposals = ouroboros.analyze_and_propose()
for proposal in proposals:
    if ouroboros.is_safe(proposal):
        ouroboros.apply(proposal)
```

---

## 13. Extending SROS

### Creating a Custom Agent

1. Create a new file in `sros/runtime/agents/`:

```python
# sros/runtime/agents/my_agent.py
from sros.runtime.agents.agent_base import AgentBase

class MyAgent(AgentBase):
    """Custom agent for specific tasks."""
    
    def __init__(self):
        super().__init__(
            name="my_agent",
            role="Custom Role",
            objective="What this agent does"
        )
    
    async def run(self, task: str, context: dict = None) -> str:
        # Your agent logic here
        prompt = self.build_prompt(task, context)
        response = await self.call_model(prompt)
        return response
```

2. Register in `sros/runtime/agents/__init__.py`

### Creating a Custom Adapter

1. Create in `sros/adapters/models/`:

```python
# sros/adapters/models/my_adapter.py
from sros.adapters.base import ModelAdapterBase

class MyAdapter(ModelAdapterBase):
    async def generate(self, prompt: str) -> str:
        # Call your model
        return response
```

2. Register in the adapter registry

### Creating Custom Policies

1. Create policy SRXML in `sros/governance/policies/`
2. Load via policy engine

---

## 14. Troubleshooting

### Common Issues

#### "Module not found" errors

```bash
# Reinstall in development mode
pip install -e .
```

#### CLI not working

```bash
# Use module path instead
python -m sros.nexus.cli.main --help
```

#### Tests failing

```bash
# Check for missing dependencies
pip install pytest pytest-asyncio

# Run specific test
pytest tests/test_kernel_boot.py -v
```

#### Memory errors

```bash
# Initialize the database
sros init

# Check memory stats
sros memory stats
```

### Debug Mode

Enable verbose logging:

```bash
sros --verbose status system
```

Or set environment variable:

```bash
set SROS_DEBUG=true
set SROS_LOG_LEVEL=DEBUG
```

### Getting Help

- Check `docs/API_REFERENCE.md` for API details
- Check `docs/CLI_GUIDE.md` for CLI commands
- Run `sros <command> --help` for command help

---

## 15. Next Steps

1. **Explore Examples**: Try the workflows in `examples/`
2. **Read Architecture**: Deep dive into `docs/ARCHITECTURE.md`
3. **Build Something**: Create your own workflow
4. **Extend SROS**: Add a custom agent or adapter
5. **Contribute**: See `CONTRIBUTING.md` for guidelines

---

## Quick Reference

### CLI Commands

| Command | Purpose |
|---------|---------|
| `sros init` | Initialize SROS |
| `sros status system` | Check system status |
| `sros agent list` | List available agents |
| `sros agent run <name> "<task>"` | Run an agent |
| `sros workflow run <file>` | Execute a workflow |
| `sros memory read --layer <layer>` | Read from memory |
| `sros memory write "<data>" --layer <layer>` | Write to memory |

### Key Files

| File | Purpose |
|------|---------|
| `sros_config.yml` | System configuration |
| `pyproject.toml` | Package definition |
| `examples/*.srxml` | Example workflows |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `SROS_DEBUG` | Enable debug mode |
| `SROS_LOG_LEVEL` | Logging level |

---

**Alpha Notice**: SROS v1 is in Alpha. APIs may change. Always review governance policies before production use.

