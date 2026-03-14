# SROS v1 User Guide

> The definitive reference for users, contributors, and operators of the
> Sovereign Runtime Operating System (SROS) v1.
>
> **Version**: 1.0.0-alpha
> **License**: MIT
> **Status**: Alpha

---

## Table of Contents

1. [What SROS v1 Is](#1-what-sros-v1-is)
2. [What This Repository Contains](#2-what-this-repository-contains)
3. [Repository Map and Folder-by-Folder Breakdown](#3-repository-map-and-folder-by-folder-breakdown)
4. [Core Concepts and Mental Model](#4-core-concepts-and-mental-model)
5. [Installation Prerequisites](#5-installation-prerequisites)
6. [Supported Environments and Python Version Guidance](#6-supported-environments-and-python-version-guidance)
7. [Install Steps from Scratch](#7-install-steps-from-scratch)
8. [Verifying a Successful Install](#8-verifying-a-successful-install)
9. [CLI Overview](#9-cli-overview)
10. [Command-by-Command Guide](#10-command-by-command-guide)
11. [First Successful Run Walkthrough](#11-first-successful-run-walkthrough)
12. [Demo Flow Walkthrough](#12-demo-flow-walkthrough)
13. [Architecture Overview](#13-architecture-overview)
14. [Package and Module Breakdown](#14-package-and-module-breakdown)
15. [SRXML Explained](#15-srxml-explained)
16. [Planes, Subsystems, and Architectural Layers](#16-planes-subsystems-and-architectural-layers)
17. [Example Workflows](#17-example-workflows)
18. [How Configuration Works](#18-how-configuration-works)
19. [Environment Variables and Secrets Handling](#19-environment-variables-and-secrets-handling)
20. [File Paths and Project-Relative Conventions](#20-file-paths-and-project-relative-conventions)
21. [Logging, Tracing, and Diagnostics](#21-logging-tracing-and-diagnostics)
22. [Test Suite Guide](#22-test-suite-guide)
23. [Development Workflow](#23-development-workflow)
24. [Contribution Workflow](#24-contribution-workflow)
25. [Branching and PR Expectations](#25-branching-and-pr-expectations)
26. [Troubleshooting and Common Failures](#26-troubleshooting-and-common-failures)
27. [Known Limitations and Honest Current Status](#27-known-limitations-and-honest-current-status)
28. [FAQ](#28-faq)
29. [Glossary](#29-glossary)
30. [Recommended Next Steps](#30-recommended-next-steps)
31. [Annotated Example Outputs](#31-annotated-example-outputs)
32. [Developer Notes on Design Philosophy](#32-developer-notes-on-design-philosophy)
33. [Public Repo Conventions and Invariants](#33-public-repo-conventions-and-invariants)
34. [How to Extend the CLI Safely](#34-how-to-extend-the-cli-safely)
35. [How to Add Tests Safely](#35-how-to-add-tests-safely)
36. [How to Update Docs Without Causing Parity Drift](#36-how-to-update-docs-without-causing-parity-drift)
37. [Release Process Guide](#37-release-process-guide)
38. [Maintenance Checklist](#38-maintenance-checklist)
39. [Security and Sanitization Guidance](#39-security-and-sanitization-guidance)

---

## 1. What SROS v1 Is

SROS (Sovereign Runtime Operating System) is an AI-native orchestration
environment that brings traditional operating system concepts - kernels,
process isolation, memory management, and governance - into the world of
Large Language Model (LLM) agents.

SROS is **not** a chatbot framework. It is not a wrapper around a single
API call. SROS is an opinionated runtime that:

- Separates agent execution from policy enforcement.
- Routes all inter-component communication through a central event bus.
- Provides tiered memory (short-term, long-term, codex, vector).
- Wraps model calls behind pluggable adapters (Gemini, OpenAI, local).
- Monitors all operations through an asynchronous observability plane.
- Supports declarative SRXML-based workflow definitions.

SROS v1 is currently in **Alpha**. The core architecture is functional
and tested. Many subsystems are present as structural scaffolds ready
for extension. This guide is honest about what works today and what
remains aspirational.

---

## 2. What This Repository Contains

The SROS-V1 repository is a single Python package published under the
name `sros`. At the root level you will find:

| Item | Type | Purpose |
|------|------|---------|
| `sros/` | Directory | The main Python package |
| `tests/` | Directory | pytest test suite |
| `docs/` | Directory | Architecture docs, study guide, API ref |
| `examples/` | Directory | Sample SRXML workflow files |
| `pyproject.toml` | File | Package metadata and dependencies |
| `sros_config.yml` | File | Default runtime configuration |
| `README.md` | File | Project overview and quickstart |
| `CONTRIBUTING.md` | File | Contributor guidelines |
| `CODE_OF_CONDUCT.md` | File | Community code of conduct |
| `CHANGELOG.md` | File | Version history |
| `RELEASE_CHECKLIST.md` | File | Release validation checklist |
| `LICENSE` | File | MIT License |
| `VERSION` | File | Canonical version string |

---

## 3. Repository Map and Folder-by-Folder Breakdown

```
SROS-V1/
├── sros/                          # Main Python package
│   ├── __init__.py                # Package root
│   ├── kernel/                    # Plane 1: System foundation
│   │   ├── kernel_bootstrap.py    # Boot sequence and KernelContext
│   │   ├── kernel_state.py        # Central state object
│   │   ├── kernel_config.py       # Config loading from YAML
│   │   ├── event_bus.py           # Pub-sub event system
│   │   ├── daemon_registry.py     # Daemon lifecycle management
│   │   └── daemons/
│   │       └── heartbeat_daemon.py
│   ├── runtime/                   # Plane 2: Agent execution
│   │   ├── workflow_engine.py     # Executes SRXML workflows
│   │   ├── session_manager.py     # Session lifecycle
│   │   ├── context_builder.py     # Prompt context assembly
│   │   ├── agents/
│   │   │   ├── agent_base.py      # Base class for all agents
│   │   │   ├── architect_agent.py # System design agent
│   │   │   ├── builder_agent.py   # Code generation agent
│   │   │   ├── tester_agent.py    # Test generation agent
│   │   │   ├── skrikx_agent.py    # Sovereign prime interface
│   │   │   └── srx_base_agent.py  # SRX-aware base agent
│   │   └── simulations/
│   │       └── sandbox.py         # Isolated execution sandbox
│   ├── governance/                # Plane 3: Policy enforcement
│   │   ├── policy_engine.py       # Policy evaluation
│   │   ├── policy_enforcer.py     # Action enforcement
│   │   ├── sovereign_directive.py # High-level directives
│   │   ├── access_control.py      # Permission control
│   │   ├── cost_tracker.py        # API cost tracking
│   │   ├── audit_log.py           # Append-only event log
│   │   └── sovereign_audit_log.py # Enhanced audit logging
│   ├── mirroros/                   # Plane 4: Observability
│   │   ├── witness.py             # Event observation and recording
│   │   ├── trace_store.py         # Trace storage backend
│   │   ├── drift_detector.py      # Behavioral drift monitoring
│   │   ├── telemetry_collector.py # Metrics collection
│   │   └── lenses.py              # Filtered views over traces
│   ├── srxml/                     # Sovereign XML subsystem
│   │   ├── parser.py              # SRXML file parser
│   │   ├── validator.py           # Schema validation
│   │   ├── models/                # Typed Python models
│   │   │   ├── srxml_base.py      # Base dataclass
│   │   │   ├── agent.py           # SRXAgent model
│   │   │   ├── workflow.py        # SR8Workflow model
│   │   │   └── policy.py          # GovernancePolicy model
│   │   ├── schemas/               # XML schema definitions
│   │   └── templates/             # Starter SRXML templates
│   ├── memory/                    # Multi-tier memory system
│   │   ├── memory_router.py       # Routes to appropriate layer
│   │   ├── short_term_memory.py   # Session-scoped store
│   │   ├── long_term_memory.py    # Persistent store
│   │   ├── codex_memory.py        # Domain knowledge store
│   │   ├── vector_store.py        # Semantic embedding store
│   │   └── backends/
│   │       └── in_memory_backend.py
│   ├── adapters/                  # Model adapter layer
│   │   ├── base.py                # Base adapter interface
│   │   ├── registry.py            # Adapter discovery and caching
│   │   └── models/
│   │       ├── gemini_adapter.py  # Google Gemini adapter
│   │       ├── openai_adapter.py  # OpenAI adapter
│   │       └── local_adapter.py   # Local model adapter
│   ├── evolution/                 # Self-improvement engine
│   │   ├── ouroboros.py           # Main loop orchestrator
│   │   ├── analyzer.py            # Behavior analysis
│   │   ├── proposer.py            # Improvement proposals
│   │   ├── observer.py            # Execution observation
│   │   └── safeguards.py          # Safety validation
│   ├── cli/                       # CLI entrypoint (shipped)
│   │   ├── main.py                # Typer app with init + run-demo
│   │   └── commands/
│   │       ├── init_sros.py       # sros init command
│   │       └── run_demo.py        # sros run-demo command
│   ├── nexus/                     # Extended CLI and API (scaffold)
│   │   ├── cli/                   # Extended CLI commands
│   │   ├── api/                   # HTTP API server
│   │   └── nexus_core.py          # Core orchestration router
│   ├── apps/                      # Demo applications
│   │   └── sros_web_nexus/        # Web-based Nexus interface
│   ├── codex/                     # Knowledge pack indexer
│   └── knowledge/                 # Bundled knowledge assets
├── tests/                         # Test suite
│   ├── fixtures/                  # Test data files
│   │   ├── sample_workflow.srxml
│   │   ├── sample_agent_prompt.srxml
│   │   ├── codex_seed.json
│   │   ├── memory_seed.json
│   │   └── policies/
│   │       └── allow_all.json
│   ├── integration/               # Integration tests (API-dependent)
│   │   ├── test_agent_gemini.py
│   │   └── test_gemini_integration.py
│   ├── test_kernel_boot.py
│   ├── test_model_adapters.py
│   ├── test_adapter_registry.py
│   ├── test_nexus_core.py
│   ├── test_ouroboros.py
│   ├── test_sovereign_directive.py
│   ├── test_srxml_parser.py
│   └── test_srxml_validator.py
├── examples/                      # Example workflow files
│   ├── hello_world_workflow.srxml
│   ├── complex_feature_workflow.srxml
│   └── sample_policy_allow_all.json
└── docs/                          # Documentation
    ├── ARCHITECTURE.md
    ├── PLANES.md
    ├── SROS_STUDY_GUIDE_v1.md
    ├── API_REFERENCE.md
    ├── CLI_GUIDE.md
    ├── DEMO.md
    └── SROS_SOVEREIGN_USER_GUIDE_v1.md
```

---

## 4. Core Concepts and Mental Model

### The Four-Plane Model

SROS organizes all functionality into four logical planes:

```
┌───────────────────────────────────────────────────────┐
│  Plane 4: MirrorOS    (Observability)                 │
│  Witnesses, traces, drift detection, telemetry        │
├───────────────────────────────────────────────────────┤
│  Plane 3: Governance  (Policy Enforcement)            │
│  Policies, cost tracking, access control, audit logs  │
├───────────────────────────────────────────────────────┤
│  Plane 2: Runtime     (Agent Execution)               │
│  Agents, workflows, sessions, context building        │
├───────────────────────────────────────────────────────┤
│  Plane 1: Kernel      (System Foundation)             │
│  Event bus, config, state, daemons                    │
└───────────────────────────────────────────────────────┘
```

**Key principles:**

- Planes communicate exclusively through the Kernel's **EventBus**.
- Governance sits synchronously above Runtime - actions are checked
  before execution.
- MirrorOS sits asynchronously alongside everything - it observes
  without blocking.
- The Kernel owns nothing domain-specific. It provides infrastructure.

### Agents Are Workers, Not Models

An Agent in SROS is not an LLM. It is a structured execution context
that may call an LLM through an adapter. Agents have:

- A defined role and objective.
- Access permissions to specific memory layers.
- A model adapter reference (which LLM to use).
- A lifecycle (instantiation, context building, execution, witnessing).

### SRXML Is the Contract Language

SRXML (Sovereign Runtime XML) is a declarative schema language for
defining agents, workflows, and policies. Rather than writing Python
code for each workflow, you author XML documents that the parser
translates into strongly typed Python dataclass objects.

### Memory Is Layered

SROS provides four memory tiers:

| Layer | Scope | Lifetime | Use Case |
|-------|-------|----------|----------|
| Short-term | Session | Session | Working context |
| Long-term | System | Persistent | Cross-session data |
| Codex | System | Persistent | Domain knowledge packs |
| Vector | System | Persistent | Semantic similarity search |

---

## 5. Installation Prerequisites

Before installing SROS, ensure you have:

- **Python 3.10 or higher**
  - Verify: `python --version`
  - SROS uses features (match-case, union types) that require 3.10+.
- **pip** (latest recommended)
  - Verify: `pip --version`
- **Git** for cloning the repository
  - Verify: `git --version`
- **(Optional) Virtual environment tool**
  - `python -m venv` or `conda`

### Optional for Full Functionality

- **Gemini API Key**: Required for Gemini model adapter tests.
  Set `GEMINI_API_KEY` in your environment or `.env` file.
- **OpenAI API Key**: Required for OpenAI model adapter tests.
  Set `OPENAI_API_KEY` in your environment or `.env` file.

Without API keys, all integration tests will be skipped automatically.
The core system boots and runs without any external API keys.

---

## 6. Supported Environments and Python Version Guidance

| Environment | Status | Notes |
|-------------|--------|-------|
| Windows 10/11 | Tested | Primary development platform |
| macOS | Expected to work | Not yet formally tested |
| Linux (Ubuntu/Debian) | Expected to work | Not yet formally tested |
| Python 3.10 | Minimum supported | |
| Python 3.11 | Tested | Primary test target |
| Python 3.12+ | Expected to work | |

SROS is a pure Python package. It has no C extensions or
platform-specific binaries. The primary dependencies are:

```
pyyaml, pydantic>=2.0, rich, aiohttp, fastapi, uvicorn,
typer, numpy, chromadb, jinja2
```

ChromaDB may install additional native dependencies (ONNX runtime)
on first use. This is handled automatically by pip.

---

## 7. Install Steps from Scratch

### Step 1: Clone the Repository

```bash
git clone https://github.com/skrikx/SROS-V1.git
cd SROS-V1
```

### Step 2: (Recommended) Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3: Install in Editable Mode

```bash
pip install -e .
```

**Expected output (last lines):**

```
Successfully installed sros-1.0.0
```

**Expected exit code:** `0`

### Step 4: Verify the CLI Is Available

```bash
sros --help
```

If `sros` is not found, ensure your virtual environment is activated
or that Python's `Scripts/` directory is in your `PATH`.

---

## 8. Verifying a Successful Install

Run the following sequence to confirm SROS is fully operational:

```bash
# 1. CLI responds
sros --help
# Expected: Shows "SROS v1 CLI" with init and run-demo commands

# 2. Tests pass
pytest tests/ -v
# Expected: 45 passed, 7 skipped, 0 errors

# 3. Package is importable
python -c "import sros; print('OK')"
# Expected: OK
```

If any step fails, consult [Troubleshooting](#26-troubleshooting-and-common-failures).

---

## 9. CLI Overview

SROS ships a CLI built on [Typer](https://typer.tiangolo.com/).
The entrypoint is defined in `pyproject.toml`:

```toml
[project.scripts]
sros = "sros.cli.main:app"
```

This means the binary `sros` is installed into your Python environment
when you run `pip install -e .`.

### Currently Shipped Commands

| Command | Description |
|---------|-------------|
| `sros init` | Initialize a new SROS environment |
| `sros run-demo` | Run the SROS demo workflow |
| `sros --help` | Show help and available commands |

### Scaffold Commands (Not Yet Wired)

The `sros/nexus/cli/` directory contains scaffold implementations for
extended commands (`agent`, `kernel`, `memory`, `status`, `workflow`).
These are **not** currently wired into the shipped CLI binary.
They exist as architectural scaffolds for future development. See
[Known Limitations](#27-known-limitations-and-honest-current-status).

---

## 10. Command-by-Command Guide

### `sros init`

**Purpose:** Initializes a new SROS environment with default
configuration and data directories.

```bash
sros init
```

**What it does:**
- Creates default configuration files if they do not exist.
- Prepares the data directory structure for memory storage.

### `sros run-demo`

**Purpose:** Runs the SROS demo workflow to verify the system boots
and agents can be dispatched.

```bash
sros run-demo
```

**What it does:**
1. Calls `kernel_bootstrap.boot()` to initialize the Kernel.
2. Starts the HeartbeatDaemon.
3. Enters a keep-alive loop (exit with `Ctrl+C`).

**Expected output:**

```
Starting SROS Demo...
Booting SROS Kernel (config=sros_config.yml)...
Starting Kernel Daemons...
  [OK] heartbeat
SROS Kernel Online.
```

### `sros --help`

**Purpose:** Displays the top-level help panel listing all available
subcommands.

```bash
sros --help
```

---

## 11. First Successful Run Walkthrough

This walkthrough takes you from a fresh clone to a confirmed working
SROS instance in under two minutes.

```bash
# Clone
git clone https://github.com/skrikx/SROS-V1.git
cd SROS-V1

# Install
pip install -e .

# Verify CLI
sros --help
# You should see "SROS v1 CLI" with init and run-demo

# Run tests to confirm integrity
pytest tests/ -v
# You should see "45 passed, 7 skipped"

# Initialize
sros init

# Run a demo
sros run-demo
# Press Ctrl+C to exit the demo loop
```

At this point, SROS is installed, verified, and operational.

---

## 12. Demo Flow Walkthrough

When you run `sros run-demo`, the following sequence executes:

```
[1] sros.cli.commands.run_demo.main() is invoked by Typer
[2] kernel_bootstrap.boot("sros_config.yml") is called
    [2a] EventBus is initialized
    [2b] MemoryRouter is initialized
    [2c] DaemonRegistry is initialized
    [2d] HeartbeatDaemon is registered and started
    [2e] kernel.ready event is published
[3] The demo enters a keep-alive loop
[4] Ctrl+C sends KeyboardInterrupt, exiting cleanly
```

The demo proves that:
- The Kernel boots from configuration.
- The EventBus is functional.
- Daemons can be registered and started.
- The system can be interrupted gracefully.

---

## 13. Architecture Overview

SROS uses a four-plane architecture with support layers underneath.

### Data Flow

```
User CLI Command
      │
      ▼
┌─────────────┐
│  Nexus/CLI  │  ─── Receives command, routes to subsystem
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Runtime   │◄───►│  Governance │  ─── Policy check before execution
│  (Agents)   │     │  (Policies) │
└──────┬──────┘     └─────────────┘
       │                   ▲
       ▼                   │
┌─────────────┐     ┌─────────────┐
│   Kernel    │◄───►│  MirrorOS   │  ─── Async observation after execution
│  (Events)   │     │  (Witness)  │
└─────────────┘     └─────────────┘
```

### Agent Execution Sequence

1. A command arrives at the Nexus layer.
2. The Runtime creates a Session and builds context.
3. Governance evaluates the proposed action against policies.
4. If allowed, the Runtime invokes the Agent.
5. The Agent calls its model adapter (Gemini, OpenAI, etc.).
6. The response flows back through the Runtime.
7. MirrorOS witnesses the entire operation asynchronously.

### Cross-Plane Communication

All planes communicate through the Kernel's EventBus:

```
Runtime  ──publish──►  EventBus  ──deliver──►  Governance
                         │
MirrorOS ◄──subscribe──  EventBus
```

No plane imports another plane directly. This enforces clean separation
and prevents circular dependencies.

---

## 14. Package and Module Breakdown

### `sros/kernel/` - Plane 1

| Module | Lines | Purpose |
|--------|-------|---------|
| `kernel_bootstrap.py` | ~34 | Boot sequence, creates KernelContext |
| `kernel_state.py` | ~80 | Central state tracking |
| `kernel_config.py` | ~60 | YAML config loading |
| `event_bus.py` | ~70 | Pub-sub event routing |
| `daemon_registry.py` | ~60 | Daemon start/stop/health |

The `KernelContext` object returned by `boot()` contains:
- `event_bus`: The EventBus instance.
- `memory`: The MemoryRouter instance.
- `registry`: The DaemonRegistry instance.

### `sros/runtime/` - Plane 2

| Module | Purpose |
|--------|---------|
| `workflow_engine.py` | Parses and executes SRXML workflow graphs |
| `session_manager.py` | Creates/manages agent sessions |
| `context_builder.py` | Assembles prompt context |
| `agents/agent_base.py` | Base class for all agents |
| `agents/architect_agent.py` | Architecture and analysis agent |
| `agents/builder_agent.py` | Code generation agent |
| `agents/tester_agent.py` | Test generation agent |

### `sros/governance/` - Plane 3

| Module | Purpose |
|--------|---------|
| `policy_engine.py` | Evaluates allow/deny/modify decisions |
| `policy_enforcer.py` | Enforces policy decisions |
| `sovereign_directive.py` | Risk-level classification |
| `cost_tracker.py` | API cost and budget tracking |
| `audit_log.py` | Append-only governance log |

### `sros/mirroros/` - Plane 4

| Module | Purpose |
|--------|---------|
| `witness.py` | Records events to trace store |
| `trace_store.py` | Underlying storage backend |
| `drift_detector.py` | Detects behavioral deviation |
| `telemetry_collector.py` | Metrics and performance data |
| `lenses.py` | Filtered views over trace data |

### `sros/adapters/` - Model Abstraction

| Module | Purpose |
|--------|---------|
| `base.py` | Abstract adapter interface |
| `registry.py` | Adapter registration, caching, tenant override |
| `models/gemini_adapter.py` | Google Gemini integration |
| `models/openai_adapter.py` | OpenAI integration |
| `models/local_adapter.py` | Local/Ollama integration |

### `sros/srxml/` - Schema Language

| Module | Purpose |
|--------|---------|
| `parser.py` | Parses `.srxml` files into dicts or typed objects |
| `validator.py` | Validates parsed objects against schema rules |
| `models/` | Dataclass definitions for Agent, Workflow, Policy |

### `sros/evolution/` - Self-Improvement

| Module | Purpose |
|--------|---------|
| `ouroboros.py` | The self-evolution loop orchestrator |
| `analyzer.py` | Identifies patterns and bottlenecks |
| `proposer.py` | Generates improvement proposals |
| `safeguards.py` | Safety checks blocking dangerous proposals |

---

## 15. SRXML Explained

SRXML (Sovereign Runtime XML) is the declarative contract language used
by SROS to define three core entity types:

### Agent Prompts (`<srx_agent_prompt>`)

```xml
<srx_agent_prompt id="agent.analyst" version="1.0" tenant="default">
    <role>analyst</role>
    <mode>read_only</mode>
    <identity>
        <system_name>AnalystAgent</system_name>
        <purpose>Ingest logs and produce summaries</purpose>
    </identity>
</srx_agent_prompt>
```

**Parsed into:** `SRXAgent` dataclass.

### Workflows (`<workflow>` or `<sr8_workflow>`)

```xml
<workflow id="test.workflow.1" name="Test Workflow">
    <step id="step1" agent="agent.test">
        <input>Hello SROS</input>
    </step>
    <step id="step2" agent="agent.test">
        <input>Step 2 Input</input>
    </step>
</workflow>
```

**Parsed into:** `SR8Workflow` dataclass.

### Governance Policies (`<governance_policy>`)

Defines allow/deny rules evaluated by the PolicyEngine.

### SRXML Lock Attributes

Every SRXML document can carry lock attributes:

| Attribute | Effect |
|-----------|--------|
| `@one_pass_lock="true"` | Prevents retries; one shot only |
| `@drift_lock="true"` | Prevents runtime mutation of parsed object |
| `@seed_lock="true"` | Fixes RNG seed for reproducibility |
| `@seed="value"` | The actual seed value |

### Using the Parser

```python
from sros.srxml.parser import SRXMLParser

parser = SRXMLParser()

# Parse to dictionary
data = parser.parse("path/to/file.srxml")

# Parse to typed object
obj = parser.parse_to_object("path/to/file.srxml")
```

---

## 16. Planes, Subsystems, and Architectural Layers

### Plane Interaction Rules

| Rule | Enforcement |
|------|-------------|
| Planes do not import each other | Structural convention |
| All cross-plane calls go through EventBus | EventBus pub-sub |
| Governance is synchronous | Blocks execution until decision |
| MirrorOS is asynchronous | Never blocks the Kernel |

### Support Layers

Support layers sit below the four planes and serve all of them:

- **SRXML**: Provides the contract language.
- **Memory**: Provides the data fabric.
- **Adapters**: Provides the model abstraction.
- **Evolution**: Provides self-improvement capabilities.
- **Nexus**: Provides the CLI/API surface.

---

## 17. Example Workflows

### `examples/hello_world_workflow.srxml`

A minimal single-task workflow:

```xml
<workflow id="hello_world" xmlns="https://sros.sros/schema/workflow">
  <task id="task_1">
    <agent>sr9_orchestrator</agent>
    <input>
      <prompt>What is the capital of France?</prompt>
    </input>
  </task>
</workflow>
```

### `examples/complex_feature_workflow.srxml`

A multi-step workflow simulating a feature implementation cycle:

```xml
<workflow id="complex.feature.flow" name="Feature Implementation Cycle">
    <identity>
        <system_name>SROS Dev Loop</system_name>
        <purpose>Simulate a full feature implementation cycle</purpose>
    </identity>

    <context>
        <item>Project: SROS v1</item>
        <item>Feature: Add Redis Memory Store</item>
    </context>

    <step id="step1" order="1">
        <agent>architect</agent>
        <instruction>Analyze the requirements for adding a
        Redis-backed memory store.</instruction>
    </step>

    <step id="step2" order="2">
        <agent>builder</agent>
        <instruction>Implement the RedisMemoryStore class.</instruction>
    </step>

    <step id="step3" order="3">
        <agent>tester</agent>
        <instruction>Generate pytest unit tests for the
        RedisMemoryStore implementation.</instruction>
    </step>
</workflow>
```

### `examples/sample_policy_allow_all.json`

A permissive test policy that allows all actions:

```json
{
  "policy_name": "allow_all_testing",
  "rules": [
    {
      "action": "*",
      "decision": "allow",
      "reason": "Testing: allow all actions"
    }
  ]
}
```

---

## 18. How Configuration Works

### Primary Configuration: `sros_config.yml`

Located at the repository root, this YAML file controls global runtime
behavior:

```yaml
mirroros:
  trace_enabled: true
  trace_path: "./data/traces"
  snapshot_interval_sec: 300

adapters:
  default_model: "gemini-pro"
  models:
    gemini-pro:
      provider: "gemini"
      api_key_env: "GEMINI_API_KEY"
    gpt-4:
      provider: "openai"
      api_key_env: "OPENAI_API_KEY"
```

### Configuration Loading

The Kernel loads configuration during boot via
`kernel_config.py`. The config path defaults to `sros_config.yml`
but can be overridden by passing a path to `kernel_bootstrap.boot()`.

---

## 19. Environment Variables and Secrets Handling

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API authentication | For Gemini adapter |
| `OPENAI_API_KEY` | OpenAI API authentication | For OpenAI adapter |
| `SROS_DEBUG` | Enable debug mode (`true`/`false`) | No |
| `SROS_LOG_LEVEL` | Log verbosity (`DEBUG`, `INFO`, `WARNING`) | No |
| `SROS_ENV` | Environment name (`dev`, `prod`) | No |
| `SROS_TENANT` | Tenant identifier for multi-tenancy | No |

### Handling Secrets Safely

- **Never commit `.env` files.** The `.gitignore` excludes `.env`.
- Store API keys in environment variables or a `.env` file.
- The `sros_config.yml` references keys by environment variable name
  (e.g., `api_key_env: "GEMINI_API_KEY"`) rather than storing them
  directly.

---

## 20. File Paths and Project-Relative Conventions

SROS uses project-relative paths throughout:

| Path | Purpose |
|------|---------|
| `./sros_config.yml` | System configuration |
| `./data/` | Runtime data (memory, traces) |
| `./tests/fixtures/` | Test data files |
| `./examples/` | Example SRXML files |

All paths will work regardless of the operating system. The
`pathlib.Path` library is used internally for cross-platform
compatibility.

---

## 21. Logging, Tracing, and Diagnostics

### MirrorOS Tracing

When `trace_enabled: true` is set in `sros_config.yml`, the Witness
component records all events to a JSONL trace file. Each trace entry
contains:

```json
{
  "timestamp": 1710448800.123,
  "event_type": "workflow.start",
  "payload": {"workflow_id": "hello_world"}
}
```

### Debug Mode

Set `SROS_DEBUG=true` in your environment to enable verbose logging
across all planes.

### Telemetry

The `TelemetryCollector` in MirrorOS records:
- Operation latencies.
- Error counts per subsystem.
- Daemon health metrics.

Access telemetry programmatically:

```python
from sros.mirroros.telemetry_collector import TelemetryCollector

collector = TelemetryCollector()
metrics = collector.get_metrics()
```

---

## 22. Test Suite Guide

### Running All Tests

```bash
pytest tests/ -v
```

**Current results (validated):**
- **45 passed**
- **7 skipped** (integration tests requiring API keys)
- **0 failed**
- **0 collection errors**
- **1 warning** (PytestCollectionWarning for TesterAgent class name)

### Test Organization

| File | Tests | What It Covers |
|------|-------|----------------|
| `test_kernel_boot.py` | 1 | Kernel boot sequence |
| `test_model_adapters.py` | 8 | Gemini, OpenAI, Local adapters |
| `test_adapter_registry.py` | 8 | Registry, caching, fallback |
| `test_nexus_core.py` | 1 | Nexus demo command dispatch |
| `test_ouroboros.py` | 8 | Evolution loop and safeguards |
| `test_sovereign_directive.py` | 4 | Risk assessment and audit |
| `test_srxml_parser.py` | 6 | SRXML parsing and object creation |
| `test_srxml_validator.py` | 6 | Schema validation rules |
| `integration/test_agent_gemini.py` | 5 | Agent + Gemini (requires key) |
| `integration/test_gemini_integration.py` | 2 | Raw Gemini calls (requires key) |

### Running Specific Tests

```bash
# Single file
pytest tests/test_kernel_boot.py -v

# Single test class
pytest tests/test_ouroboros.py::TestOuroborosLoop -v

# Only integration tests
pytest tests/integration/ -v

# Exclude integration tests
pytest tests/ -v --ignore=tests/integration/
```

---

## 23. Development Workflow

### Daily Development Loop

1. Pull latest changes from `main`.
2. Activate your virtual environment.
3. Make changes to the relevant plane directory.
4. Run related tests: `pytest tests/test_<module>.py -v`
5. Run full suite: `pytest tests/ -v`
6. Commit with a descriptive message.

### Code Style

SROS follows PEP 8 with these conventions:

- Maximum line length: 100 characters.
- Google-style docstrings.
- Type hints on all public functions.
- Imports grouped: stdlib, third-party, local.

### Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Modules | `snake_case` | `kernel_state.py` |
| Classes | `PascalCase` | `KernelState` |
| Functions | `snake_case` | `get_state()` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES` |

---

## 24. Contribution Workflow

1. Fork the repository (or create a feature branch).
2. Clone and install in editable mode:
   ```bash
   git clone <your-fork-url>
   cd SROS-V1
   pip install -e .
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```
4. Make changes, add tests, update docs.
5. Run the full test suite:
   ```bash
   pytest tests/ -v
   ```
6. Commit and push:
   ```bash
   git add .
   git commit -m "feat: description of change"
   git push origin feature/my-feature
   ```
7. Open a Pull Request against `main`.

See `CONTRIBUTING.md` for detailed code style guidelines, SRXML
authoring rules, and plane-specific contribution rules.

---

## 25. Branching and PR Expectations

### Branch Naming

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/redis-memory` |
| `fix/` | Bug fixes | `fix/kernel-boot-crash` |
| `docs/` | Documentation only | `docs/update-cli-guide` |

### PR Requirements

- All tests must pass (`pytest tests/ -v`).
- New code must include corresponding tests.
- Documentation must be updated if public behavior changes.
- CHANGELOG.md should be updated.
- PR description should list affected planes.

---

## 26. Troubleshooting and Common Failures

### `ModuleNotFoundError: No module named 'sros'`

**Cause:** The package is not installed, or the virtual environment
is not activated.

**Fix:**
```bash
pip install -e .
```

### `sros: command not found`

**Cause:** The CLI binary is not in your PATH.

**Fix:**
```bash
# Use the module path instead
python -m sros.cli.main --help

# Or ensure your venv Scripts/ directory is in PATH
```

### `pip install` fails with multiple top-level packages

**Cause:** A stale `sros.egg-info` or conflicting package metadata.

**Fix:**
```bash
rm -rf sros.egg-info
pip install -e .
```

### Integration tests all skip

**Cause:** No `GEMINI_API_KEY` or `OPENAI_API_KEY` set.

**Fix:** This is expected behavior. Integration tests require
external API keys. Set the relevant environment variable to run them.

### `PytestCollectionWarning: cannot collect test class 'TesterAgent'`

**Cause:** The class `TesterAgent` starts with "Test", which pytest
tries to collect. Since it has an `__init__`, pytest skips it with
a warning.

**Impact:** None. This is cosmetic. All tests pass normally.

---

## 27. Known Limitations and Honest Current Status

### What Works Today (Alpha)

| Feature | Status | Evidence |
|---------|--------|----------|
| Kernel boot and EventBus | Working | `test_kernel_boot.py` passes |
| SRXML parsing and validation | Working | 12 parser/validator tests pass |
| Model adapter abstraction | Working | 11 adapter tests pass |
| Ouroboros safeguards | Working | 8 evolution tests pass |
| Sovereign directives | Working | 4 directive tests pass |
| CLI (`init`, `run-demo`) | Working | `sros --help` verified |
| Package install | Working | `pip install -e .` exit code 0 |

### What Is Scaffold-Only (Future)

| Feature | Current State |
|---------|---------------|
| Extended CLI (`agent`, `kernel`, `memory`, `workflow`) | Code exists in `sros/nexus/cli/` but is not wired to the shipped CLI |
| HTTP API server | Scaffolded in `sros/nexus/api/` but not launched |
| Full workflow execution with live LLM calls | WorkflowEngine exists but requires a Witness and adapters to be wired |
| ChromaDB vector memory | Dependency installed but backend integration is minimal |
| Drift detection with real semantic analysis | DriftDetector class exists but thresholds are not calibrated |
| Web Nexus UI | React/TypeScript scaffold in `sros/apps/sros_web_nexus/ui/` |

### Honest Assessment

SROS v1 is a well-structured Alpha release. The architecture is
sound, the four-plane model is enforced in code, and the test suite
provides baseline confidence. The system is best understood as an
**architectural proof-of-concept with real tested infrastructure**.
Production deployment of LLM agent workflows will require
completing the scaffold-to-live wiring described above.

---

## 28. FAQ

### Q: Can I use SROS without any API keys?

**A:** Yes. The Kernel boots, the EventBus runs, and all unit tests
pass without any external API keys. Only integration tests (marked
with `skipUnless`) require keys.

### Q: Which LLM does SROS use by default?

**A:** The default model is configured as `gemini-pro` in
`sros_config.yml`. You can change this to `gpt-4` or any adapter
registered in the `AdapterRegistry`.

### Q: Is SROS a web application?

**A:** Not primarily. SROS is a Python CLI application and library.
There is a scaffolded FastAPI server in `sros/nexus/api/` and a
React UI scaffold in `sros/apps/sros_web_nexus/ui/`, but these are
not yet wired for production use.

### Q: Can I add my own agents?

**A:** Yes. Create a new class extending `AgentBase` in
`sros/runtime/agents/`. Define its role, objective, and model
adapter reference. Register it in the agents `__init__.py`.

### Q: What Python version do I need?

**A:** Python 3.10 or higher. Tested primarily on Python 3.11.

### Q: Why XML and not JSON or YAML for schemas?

**A:** SRXML provides strict structural contracts with attributes,
lock semantics, and namespace support. XML is more rigid than JSON
for enforcing document-level constraints, which aligns with SROS's
sovereignty-first philosophy.

### Q: Is there a Docker image?

**A:** Not yet. SROS v1 is distributed as a Python source package.
A Dockerfile may be added in a future release.

---

## 29. Glossary

| Term | Definition |
|------|------------|
| **Agent** | A structured execution context that may invoke an LLM through an adapter. Has a role, objective, and permissions. |
| **Adapter** | An abstraction layer between SROS and an external LLM provider (Gemini, OpenAI, local). |
| **EventBus** | The central pub-sub message routing system inside the Kernel. All inter-plane communication flows through it. |
| **Governance** | Plane 3. Evaluates proposed actions against policies before allowing execution. |
| **Kernel** | Plane 1. The foundational backbone managing events, config, state, and daemons. |
| **KernelContext** | The object returned by `kernel_bootstrap.boot()` containing the event bus, memory, and daemon registry. |
| **MirrorOS** | Plane 4. The asynchronous observability layer that records all system events without blocking execution. |
| **Nexus** | The CLI and API surface layer that routes user commands to the appropriate SROS subsystem. |
| **One Pass Lock** | An SRXML attribute that prevents an agent from retrying. It must succeed or fail in a single pass. |
| **Ouroboros** | The self-evolution engine. Analyzes, proposes, validates, and applies improvements to the codebase. |
| **Receipt** | A verifiable proof of completion: test pass log, trace hash, or audit entry. |
| **Runtime** | Plane 2. The execution environment where agents process tasks and produce outputs. |
| **SRXML** | Sovereign Runtime XML. The declarative schema language for defining agents, workflows, and policies. |
| **Sovereign Directive** | A risk-classified action evaluation. Low-risk actions auto-proceed; high-risk actions require operator approval. |
| **Witness** | The MirrorOS component that observes events and writes them to a trace store. |

---

## 30. Recommended Next Steps

### For Users

1. Complete the [First Successful Run](#11-first-successful-run-walkthrough).
2. Read the `examples/` directory and understand the SRXML structure.
3. Explore `sros_config.yml` and customize adapter settings.
4. Run `pytest tests/ -v` to understand the test coverage.

### For Contributors

1. Read `CONTRIBUTING.md` for coding standards.
2. Study `docs/ARCHITECTURE.md` for the data flow diagrams.
3. Pick an open issue or scaffold module to wire up.
4. Write tests first, then implement.

### For Operators

1. Configure `sros_config.yml` with your API keys and budget limits.
2. Review the Governance plane policies before deploying agents.
3. Monitor `sros_traces.jsonl` for operational anomalies.
4. Use the Ouroboros safeguards to evaluate proposed self-modifications.

---

## 31. Annotated Example Outputs

### Kernel Boot Output

```
Booting SROS Kernel (config=sros_config.yml)...   # [1] Config loaded
Starting Kernel Daemons...                         # [2] Registry iterates
  [OK] heartbeat                                   # [3] Daemon started
SROS Kernel Online.                                # [4] kernel.ready published
```

### pytest Output

```
tests/test_kernel_boot.py::test_kernel_boot PASSED           # Kernel plane verified
tests/test_model_adapters.py::TestGeminiAdapter::... PASSED  # Adapter mocking verified
tests/test_ouroboros.py::TestOuroborosLoop::... PASSED       # Evolution safeguards verified
tests/test_srxml_parser.py::TestSRXMLParser::... PASSED      # SRXML parsing verified
```

---

## 32. Developer Notes on Design Philosophy

### Why Four Planes?

The four-plane model is inspired by traditional OS kernel
architecture (ring 0, ring 3) but adapted for AI systems:

- **Separation of concerns**: An agent cannot modify the policy
  that governs it.
- **Independent evolution**: Each plane can be upgraded without
  affecting others.
- **Testability**: Each plane can be tested in isolation.

### Why Not a More Complex Agent Framework?

SROS intentionally avoids the "framework of frameworks" trap.
The agent system is deliberately simple: `AgentBase` provides a
standardized lifecycle, and model calls are routed through adapters.
Complex multi-agent topographies are expressed in SRXML workflows,
not in deeply nested Python class hierarchies.

### Why XML Instead of JSON Schemas?

SRXML's use of XML is a deliberate architectural choice:
- XML attributes provide metadata (`id`, `version`, `tenant`)
  without conflating them with content.
- XML namespaces prevent collision in multi-tenant environments.
- XML schema validation is more mature than JSON Schema tooling.
- Lock attributes (`one_pass_lock`, `drift_lock`) enforce
  execution semantics at the document level.

---

## 33. Public Repo Conventions and Invariants

### Files That Must Always Exist

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package definition |
| `README.md` | Project entry point |
| `LICENSE` | MIT license text |
| `sros_config.yml` | Default configuration |

### Files That Must Never Be Committed

| Pattern | Reason |
|---------|--------|
| `.env` | Contains secrets |
| `*.log` | Runtime artifacts |
| `*.jsonl` | Trace data |
| `__pycache__/` | Python bytecode cache |
| `sros.egg-info/` | Build artifacts |

---

## 34. How to Extend the CLI Safely

The shipped CLI is defined in `sros/cli/main.py` using Typer:

```python
import typer
from .commands.init_sros import app as init_app
from .commands.run_demo import app as run_demo_app

app = typer.Typer()
app.add_typer(init_app, name="init")
app.add_typer(run_demo_app, name="run-demo")
```

### Adding a New Command

1. Create `sros/cli/commands/my_command.py`:
   ```python
   import typer
   app = typer.Typer()

   @app.callback(invoke_without_command=True)
   def main():
       """My new SROS command."""
       print("Hello from my command")
   ```

2. Register in `sros/cli/main.py`:
   ```python
   from .commands.my_command import app as my_app
   app.add_typer(my_app, name="my-command")
   ```

3. Reinstall: `pip install -e .`
4. Test: `sros my-command`

---

## 35. How to Add Tests Safely

### Test File Naming

All test files must match the pattern `test_*.py` as configured
in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

### Test Structure

```python
import pytest

class TestMyFeature:
    """Tests for my feature."""

    def test_basic_functionality(self):
        """Feature should do X when given Y."""
        result = my_function(input_data)
        assert result == expected_output

    def test_error_handling(self):
        """Feature should raise ValueError on bad input."""
        with pytest.raises(ValueError):
            my_function(None)
```

### Fixture Files

Place test data in `tests/fixtures/`. Reference using:

```python
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
data_file = fixtures_dir / "my_data.json"
```

---

## 36. How to Update Docs Without Causing Parity Drift

### The Parity Rule

Every public-facing document must match the current code. If you
change a CLI command, the following docs must be updated:

1. `README.md` - CLI Commands section
2. `docs/CLI_GUIDE.md` - Full CLI reference
3. `docs/USER_GUIDE.md` (this document) - Sections 9, 10, 11

### Verification

After updating docs, run:

```bash
# Confirm CLI matches docs
sros --help

# Confirm tests still pass
pytest tests/ -v
```

---

## 37. Release Process Guide

### Pre-Release Checklist

1. All tests pass: `pytest tests/ -v`
2. CLI responds: `sros --help`
3. Package installs cleanly: `pip install -e .`
4. No secrets in tracked files.
5. `VERSION` file matches `pyproject.toml` version.
6. `CHANGELOG.md` is updated.
7. `README.md` reflects current capabilities only.

### Version Bump

1. Update `VERSION` file.
2. Update `version` in `pyproject.toml`.
3. Add entry to `CHANGELOG.md`.
4. Commit: `git commit -m "release: v1.0.1"`
5. Tag: `git tag v1.0.1`
6. Push: `git push --tags`

---

## 38. Maintenance Checklist

### Weekly

- [ ] Run `pytest tests/ -v` and confirm no regressions.
- [ ] Check `.gitignore` for any new artifact patterns.
- [ ] Review open issues and PRs.

### Monthly

- [ ] Audit dependencies: `pip list --outdated`
- [ ] Review MirrorOS traces for anomalous patterns.
- [ ] Update CHANGELOG if changes were made.

### Per-Release

- [ ] Full release checklist in `RELEASE_CHECKLIST.md`.
- [ ] Verify no secrets leaked via `git log --all -S "API_KEY"`.
- [ ] Confirm package installs fresh in a clean venv.

---

## 39. Security and Sanitization Guidance

### Secret Management

- API keys belong in `.env` or system environment variables only.
- The `.gitignore` blocks `.env` from being tracked.
- `sros_config.yml` references keys by env var name, never by value.

### Pre-Release Sanitization

Before any public push, verify:

```bash
# Search for potential leaked secrets
git log --all -S "AIzaSy" --oneline
git log --all -S "sk-" --oneline

# Search for local user paths
git grep -l "C:\\Users\\"
git grep -l "/home/"

# Search for email addresses
git grep -lE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
```

### Path Sanitization

SROS should never contain hardcoded absolute paths in tracked files.
All paths should be relative to the project root or constructed
using `pathlib.Path(__file__).parent`.

---

*End of SROS v1 User Guide.*
*Generated from repository truth. Validated against live install, CLI,
and test receipts.*
