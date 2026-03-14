# SROS v1: Apex Grade Sovereign User Guide

> **Document Classification**: Sovereign Grade
> **Subject**: The Definitive SROS v1 Operations, Architecture, and Technical Manual
> **Author**: Antigravity (Sovereign SROS Builder Agent)
> **Version**: 1.0.0
> **Scope**: Encompasses all technical, architectural, operational, and policy domains.

---

## 📜 Table of Contents

1. [Introduction to the Sovereign Runtime Operating System (SROS)](#1-introduction-to-the-sovereign-runtime-operating-system-sros)
2. [The Core Philosophy of Sovereignty](#2-the-core-philosophy-of-sovereignty)
3. [The Four-Plane Architecture: A Deep Dive](#3-the-four-plane-architecture-a-deep-dive)
    - [3.1 Plane 1: Kernel (The Foundation)](#31-plane-1-kernel-the-foundation)
    - [3.2 Plane 2: Runtime (The Execution Hub)](#32-plane-2-runtime-the-execution-hub)
    - [3.3 Plane 3: Governance (The Absolute Authority)](#33-plane-3-governance-the-absolute-authority)
    - [3.4 Plane 4: MirrorOS (The Omniscient Observer)](#34-plane-4-mirroros-the-omniscient-observer)
4. [The Data Fabric: Multi-Tiered Memory & Persistence](#4-the-data-fabric-multi-tiered-memory--persistence)
5. [The Semantic Schema: SRXML & Determinism](#5-the-semantic-schema-srxml--determinism)
6. [Self-Evolution: The Ouroboros Engine](#6-self-evolution-the-ouroboros-engine)
7. [Operational Guide: Installation, Configuration, and CLI](#7-operational-guide-installation-configuration-and-cli)
8. [Developer Guide: Extending and Customizing SROS](#8-developer-guide-extending-and-customizing-sros)
9. [Advanced Troubleshooting and System Recovery](#9-advanced-troubleshooting-and-system-recovery)
10. [Glossary of Terms](#10-glossary-of-terms)

---

## 1. Introduction to the Sovereign Runtime Operating System (SROS)

The Sovereign Runtime Operating System (SROS v1) is not merely a framework or a library for making REST API calls to Large Language Models. It is a revolutionary, AI-native virtualization environment designed to elevate raw, non-deterministic AI generation into Sovereign, autonomous, and strictly governed agentic workflows. 

Traditional AI applications suffer from severe architectural flaws: they lack deterministic execution bounds, struggle with multi-agent state persistence, and rely on fragile "prompt engineering" to prevent malicious behavior. SROS completely reimagines this paradigm by applying standard operating system principles—such as kernels, process isolation, memory management, and hardware abstraction—directly into the cognitive space.

By wrapping AI execution within a strict, verifiability-first architecture, SROS guarantees determinism, absolute safety, and the ability for continuous, supervised self-evolution. SROS owns the memory, the governance, and the orchestration; the AI models themselves are merely interchangeable adapters plugged into the Sovereign engine.

---

## 2. The Core Philosophy of Sovereignty

SROS v1 is built upon a foundation of unyielding, non-negotiable tenets. These tenets are not suggestions; they are the physical laws of the system.

### 2.1 Receipts-First Validity
No automated action, mutation, or configuration change within SROS is considered legitimate or complete without a cryptographically sound or test-driven receipt. If an agent refactors code, it must procure a `pytest` receipt proving determinism. If the Governance plane blocks an action, it must procure a JSONL audit trace. Claims of success without receipts are classified as hallucinations and are rolled back.

### 2.2 Determinism Sacred
LLMs are inherently non-deterministic. SROS forces them into deterministic bounds. All execution environments, agent roles, memory boundaries, and parsed variables must remain consistent. If identical AI inputs and architectural states are provided to the Kernel, the resulting systemic behavior and policy execution must be identical. There is no tolerance for mixed execution modes or silent semantic drift.

### 2.3 Sovereign Governance
No action—whether initiated by a human operator, a scheduled daemon, or a Prime Agent—bypasses the Governance plane. The Policy Engine sits synchronously above all execution. It enforces hardcoded limits, budget constraints, and risk thresholds before any computational cycles are wasted.

### 2.4 Truth from Code
Documentation, policies, and systemic state are never abstract concepts existing outside the system. They are strictly derived from live execution paths. SROS demands that the "Truth" of the system is what is presently compiling and passing validations, never what is written in a stagnant markdown template.

---

## 3. The Four-Plane Architecture: A Deep Dive

SROS completely decouples system components into a strictly layered hierarchy. This guarantees high cohesion, low coupling, and the prevention of catastrophic AI drift. The architecture is segregated into four primary planes: Kernel, Runtime, Governance, and MirrorOS.

### 3.1 Plane 1: Kernel (The Foundation)

**Location:** `sros/kernel/`

The Kernel plane serves as the absolute bedrock of the entire SROS ecosystem. Everything else—from the most complex LLM inference to the simplest logging command—is a client of the Kernel. Without the Kernel, the Runtime has no reality.

#### 3.1.1 Kernel Boot Sequence (`kernel_bootstrap.py`)
When the SROS binary is invoked, the Kernel boot sequence explicitly follows the configuration defined in `sros_config.yml`.
1. **Event Bus Initialization**: The system boots a lightweight, hyper-fast asynchronous pub-sub message router. This `EventBus` handles all intra-plane communications, ensuring that no plane tightly couples to another via direct Python class instantiations.
2. **Memory Router Mount**: Attaches the defined memory tiers (Short-term, Long-term, Codex, Vector) into a single unified `MemoryRouter`, preparing the data fabric for agent consumption.
3. **Daemon Registry Alignment**: Initializes background systemic processes, starting with the core `HeartbeatDaemon` to ensure liveness and system health tracking.
4. **State Finalization**: The `KernelState` object locks in the active topology, broadcasting the `kernel.ready` event across the bus.

#### 3.1.2 The Event Bus Protocol
The `EventBus` is the central nervous system. When the Runtime plane wishes to execute an agent, it publishes an `agent.action_proposed` event. It does not call the agent directly. The Governance plane subscribes to this topic, intercepts the event, evaluates the action against the current XML policy trees, and then either publishes a `policy.action_allowed` or `policy.action_denied` event back to the bus.

---

### 3.2 Plane 2: Runtime (The Execution Hub)

**Location:** `sros/runtime/`

The Runtime is the user-space where cognitive processes occur. It is the only plane permitted to interact with external LLMs via out-of-band `adapters`. This plane acts as the physics engine for the AI world.

#### 3.2.1 Agent Typologies (`AgentBase`)
SROS comes pre-equipped with foundational Agent topologies, all inheriting from base abstractions that enforce strict state lifecycles:
- **ArchitectAgent**: Responsible for scoping system design, proposing broad schemas, performing root-cause analysis on systemic failures, and building implementation plans. Focuses on structural integrity over code syntax.
- **BuilderAgent**: An execution-focused engine. Writes, refactors, and deploys actual code iterations bounded strictly by SRXML templates.
- **TesterAgent**: The quality-assurance oracle. Writes and executes `pytest` harnesses against the code generated by the Builder. It procures the receipts required by the One Pass Lock mandate.
- **SkrikxAgent (Prime)**: The master orchestrator representing the Sovereign Prime interface, capable of observing the lower agents, re-routing context, and dispatching complex sub-workflows.

#### 3.2.2 Workflow Orchestration (`workflow_engine.py`)
The `WorkflowEngine` consumes `SR8Workflow` XML models. It guarantees that multi-agent steps are evaluated sequentially or conditionally based on the DAG (Directed Acyclic Graph) defined in the XML. A workflow orchestrates multiple agents, passing conversational contexts and serialized memory natively between disparate models, ensuring long-running processes do not lose coherency.

#### 3.2.3 Model Agnostic Adapters (`sros/adapters/`)
LLM APIs are abstracted behind the `AdapterRegistry`. An operator can seamlessly shift a running instance from OpenAI (`gpt-4o`) to Google (`gemini-1.5-pro`) to local inferences (`Ollama`) without refactoring any runtime code. The adapters normalize all prompt outputs into a standard SROS envelope, ensuring the Workflow Engine never has to deal with vendor-specific JSON structures.

---

### 3.3 Plane 3: Governance (The Absolute Authority)

**Location:** `sros/governance/`

SROS does not rely on fragile "prompt engineering" (e.g., telling the model "Please do not delete files") to keep the host system safe. SROS relies on synchronous execution locks enforced directly by Plane 3.

#### 3.3.1 The Policy Engine
The `PolicyEngine` listens for `agent.action_proposed` events on the bus. Before the Runtime plane is allowed to invoke an adapter, the proposed action is parsed against all active `GovernancePolicy` rulesides (written in SRXML).
- **Hard Sandbox Limits**: An XML policy might declare absolute restrictions, such as blocking all file writes to the `kernel/` directory. If a BuilderAgent hallucinates and attempts to format the Kernel, the `PolicyEngine` instantly intercepts and destroys the request, logging the violation.
- **Financial Controls**: Tracked by the `CostTracker`, the engine calculates the estimated token usage of an agent's request. If the daily API budget is breached, the action is denied with an `InsufficientFunds` exception.

#### 3.3.2 Sovereign Directives & Risk Assessment
The `SovereignDirective` system ranks actions by quantitative risk.
- **Low Risk** (e.g., Reading a public file, querying a local database): Auto-allowed and logged to the asynchronous audit trail.
- **Medium Risk** (e.g., Spawning a temporary sandbox, writing to `tmp/`): Evaluated against current system load and context.
- **High Risk** (e.g., Code Execution outside Sandbox, Destructive Deletes, Modifying Policies): Generates a systemic lock requiring explicit, cryptographic Hassan (Operator) intervention or an advanced pre-approved receipt chain.

#### 3.3.3 The Append-Only Audit Log
Every decision made by the Policy Engine, whether an allowance or a denial, is sequentially written to the `SovereignAuditLog`. This log is immutable during runtime and serves as the ultimate source of truth for forensic analysis if an agentic workflow breaches expected behavior.

---

### 3.4 Plane 4: MirrorOS (The Omniscient Observer)

**Location:** `sros/mirroros/`

Where Governance acts synchronously *before* the action to prevent catastrophe, MirrorOS acts asynchronously *after* the action to establish absolute observability and non-repudiation.

#### 3.4.1 The Witness (`witness.py`)
Every `publish()` on the Kernel's Event Bus is intercepted by the Witness. The Witness wraps these events in a temporal envelope, assigning high-precision timestamps and tracking IDs, and serializes them in JSONL format to `sros_traces.jsonl`. This establishes a complete "flight recorder" for the SROS instance.

#### 3.4.2 Drift Detection & Telemetry
MirrorOS monitors the divergence between internal states and outputted realities. 
- The `DriftDetector` acts as an immune system, logging discrepancies between expected codebase outputs and external runtime configurations. If configuration drift exceeds predefined thresholds (e.g., parsed dataclass schemas no longer match the live Python classes), the drift lock engages, halting the system and enforcing a rollback to the last verified receipt.
- The `TelemetryCollector` gathers metrics on latency, token throughput, subsystem health, and active daemon loads, making them available for querying via lenses.

#### 3.4.3 Observational Lenses
Lenses provide customizable filters over the raw Witness data, allowing operators to query the system's history through specific paradigmatic views:
- **Temporal Lens**: Compares current behavior to historical execution traces to detect performance regressions.
- **Identity Lens**: Verifies that an agent mapping strictly adheres to its SRXML `role` and `mode`.
- **Risk Lens**: Highlights vectors of potential systemic harm over extended workflow periods.

---

## 4. The Data Fabric: Multi-Tiered Memory & Persistence

**Location:** `sros/memory/`

SROS owns memory outright. AI models are stateless function calls; SROS is the stateful environment. Memory is meticulously tiered and automatically routed to balance I/O speed, persistence, and semantic recall via the `MemoryRouter`.

1. **Short-Term Memory**: In-memory, dictionary-backed data stores spanning the lifespan of a single Session. Ideal for rapid conversation histories and immediate context passing between sequential agent steps. Exits existence upon `session.close()`.
2. **Long-Term Memory**: Disk-backed (SQLite/JSON) storage. Data persists between reboots, preserving user preferences, historical configurations, and explicit system parameters.
3. **Codex Memory**: A highly specialized layer representing the exact map of the codebase geometry. Responsible for knowing which abstract files map to which classes, caching abstract syntax trees, and preventing agents from hallucinating file paths.
4. **Vector Store**: A continuous semantic space (backed theoretically by ChromaDB) allowing context-aware embedding queries. Retrieves past architectural decisions, previous bugs, and deeply buried context based on high-dimensional similarity.

---

## 5. The Semantic Schema: SRXML & Determinism

**Location:** `sros/srxml/`

SROS violently rejects arbitrary JSON schema drift. LLMs output unpredictable JSON structures, which leads to `KeyError` crashes in production. SROS solves this by utilizing Sovereign XML (SRXML). All logical entities are strongly typed, heavily locked XML files parsed into strict Pydantic/Dataclass objects.

### 5.1 Document Topologies
- `<srx_agent_prompt>`: Governs an Agent's identity, role, permissions, context bindings, and core objectives.
- `<sr8_workflow>`: Outlines a strict progression of tasks, dependencies, injected inputs, and expected output contracts.
- `<governance_policy>`: Establishes a sandbox limit constraint, defining the condition, the action (`allow` or `deny`), and the explicit notification message.

### 5.2 The Lock System
Every SRXML document carries rigid systemic attributes that enforce the OS's laws:
- `@one_pass_lock='true'`: Restricts loop executions. If an agent fails a step with this lock active, it is not permitted to request manual human guidance. It must read the logs, synthesize a fix, and complete the objective in a single autonomous pass.
- `@drift_lock='true'`: Enforces absolute immutability after parsing. The parsed object cannot be dynamically mutated at runtime.
- `@seed_lock`: Ensures that the random generation seed for any LLM calls executed under this document is fixed, guaranteeing absolute reproducibility.

### 5.3 Parsing and Validating
The `SRXMLParser` reads the raw XML and translates `item` nodes into lists, enforcing required schema tags. The parsed objects are then validated by the `SRXMLValidator` before the Kernel allows them to enter the Runtime plane.

---

## 6. Self-Evolution: The Ouroboros Engine

**Location:** `sros/evolution/`

The `OuroborosLoop` represents SROS’s crowning theoretical capability: the capacity to analyze, refactor, and optimize its own source code within hyper-strict Sovereign guidelines.

### 6.1 The Evolutionary Pipeline
1. **Observation & Signals**: MirrorOS observes poor latency, redundant code paths, or unoptimized loops natively.
2. **Analysis Phase**: The `Analyzer` identifies structural bottlenecks and packages the telemetry.
3. **Proposer Phase**: An internal Analyst Agent writes an `EvolutionProposal` outlining a localized optimization, adhering to the "Minimal Diff Bias" operating law.
4. **Safeguard Interception**: The proposal is subjected to `Safeguards.check_proposal_allowed()`. It maps bounding boxes (e.g., "Does this touch Plane 1?", "Are edits > 50 lines?"). If it hits a forbidden zone, the proposal is vaporized.
5. **Implementation Sandbox**: The proposal is executed to an isolated sandbox environment, detached from the live Kernel.
6. **Validation & Integration**: SROS generates aggressive `pytest` suites against the sandbox. If the tests fail, the rollback is instantaneous, and the error traces are fed back to the Proposer. If passed with a cleanly verified receipt, it merges into the mainline code.

---

## 7. Operational Guide: Installation, Configuration, and CLI

### 7.1 Quick Installation via Source
SROS v1 is designed for UNIX and Windows environments running Python 3.10+.
```bash
git clone https://github.com/skrikx/SROS-V1.git
cd SROS-V1
python -m pip install -e .
```

### 7.2 Core Configuration (`sros_config.yml`)
The operating parameters of the entire system are determined by the YAML config file located at the repository root.
```yaml
system:
  mode: apex
  runtime: default

kernel:
  tick_rate_ms: 10
  max_daemons: 10

memory:
  short_term: "memory.short"
  max_tokens: 16384

adapters:
  default_model: "gemini"
  
governance:
  enforce_policies: true
  cost_budget_daily: 50.0
```

### 7.3 Environmental Variables
Essential secrets and toggles are managed via `.env` or system variables:
- `GEMINI_API_KEY`: Authentication for Google's Gemini endpoint.
- `OPENAI_API_KEY`: Authentication for OpenAI endpoints.
- `SROS_DEBUG`: Set to `true` to enable verbose stack traces.
- `SROS_LOG_LEVEL`: Adjust logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

### 7.4 Command Line Interface (Nexus CLI)
The SROS binary exposes standard operations directly to the operator. The CLI acts as the entrypoint to the Nexus Core API.

#### 7.4.1 System Commands
- **`sros init`**: Initializes configurations, scaffolds local memory SQLite stores, and verifies all cryptographic dependencies.
- **`sros run-demo`**: Executes the foundational `Canonical Demo` workflow (simulating basic Plane-to-Plane communication) to verify the Kernel boots correctly and Agents can pass contexts natively.

*(Note: Advanced commands such as `sros agent run` and `sros memory read` are currently handled either via internal workflows or direct Python API integrations in v1).*

---

## 8. Developer Guide: Extending and Customizing SROS

SROS is designed to be highly modular. Developers can extend the system by writing new Adapters, Agents, and Policies.

### 8.1 Crafting a Custom Agent
To create a custom LLM archetype, you do not write Python prompts. You write an SRXML template. Hand this SRXML to the `WorkflowEngine` to spawn the customized identity.

```xml
<srx_agent_prompt id="agent.my_custom_analyst" version="1.0" tenant="custom">
    <role>analyst</role>
    <mode>read_only</mode>
    <identity>
        <system_name>AnalystAgent</system_name>
        <purpose>Ingest large log files and output structured JSON summaries</purpose>
    </identity>
    <objectives>
        <item>Never mutate state</item>
        <item>Always provide line numbers</item>
    </objectives>
</srx_agent_prompt>
```

### 8.2 Interfacing with Nexus in Python
You can embed SROS inside broader applications by bypassing the CLI and interacting directly with the `NexusCore`.

```python
from sros.kernel import kernel_bootstrap
from sros.apps.sros_web_nexus.nexus_core import NexusCore

# 1. Boot the OS
kernel_context = kernel_bootstrap.boot("sros_config.yml")

# 2. Attach the Nexus Router
nexus = NexusCore(kernel_context)

# 3. Dispatch high-level commands
response = nexus.run_command("run_demo")
print(f"Status: {response['status']}")

# 4. Graceful Shutdown
kernel_context.registry.stop_all()
```

### 8.3 Implementing a New Model Adapter
To add support for a fictional new LLM provider (e.g., `Anthropic`), inherit from `ModelAdapterBase` in `sros/adapters/models/`.

```python
from sros.adapters.base import ModelAdapterBase

class AnthropicAdapter(ModelAdapterBase):
    async def generate(self, prompt: str) -> str:
        # Implement proprietary HTTP call here
        pass
        
    async def estimate_cost(self, prompt: str) -> float:
        # Implement token math
        return count * 0.0001
```
Register the adapter in the `AdapterRegistry`, and the Runtime plane will automatically be able to utilize Claude models.

---

## 9. Advanced Troubleshooting and System Recovery

When the operating system enters a failure state, SROS relies on deterministic logs to recover.

### 9.1 Diagnosing Kernel Panics
If `sros run-demo` hangs or crashes immediately upon booting:
1. Enable `SROS_DEBUG=true`.
2. Check `harness.log` for EventBus timeouts.
3. Ensure the `HeartbeatDaemon` successfully registered in the pre-flight checks. A blocked port or thread deadlock in the memory router will prevent the daemon from ticking.

### 9.2 Tracing Agent Hallucinations
If an Agent begins emitting anomalous outputs or failing workflow steps:
1. Examine `sros_traces.jsonl` via MirrorOS. Look for the `agent.thinking` and `agent.acted` events.
2. Cross-reference the timestamps with `sros_audit.jsonl` to ensure the Governance plane did not forcefully modify the prompt context due to a policy violation.
3. Check the `DriftDetector` logs. If the LLM drifted away from the SRXML `<output_contract>`, SROS will silently retry up to the retry limit before hard-failing.

### 9.3 Resolving SQLite Memory Locks
If `MemoryRouter` throws `database is locked` exceptions during highly parallel workflows:
1. Ensure the `long_term_memory` configuration path is located on a local drive, not a high-latency network share.
2. In SROS v1, avoid spawning more than 5 highly-active agents simultaneously against a single SQLite endpoint without enabling WAL (Write-Ahead Logging) mode.

---

## 10. Glossary of Terms

- **Apex Grade**: The absolute highest standard of SROS development. Requires strict One Pass Lock obedience, unyielding adherence to computational reality, and the absolute removal of all placeholder variables or mock architectures.
- **One Pass Lock**: A rigid agent execution restriction whereby the system is not permitted to request manual human guidance. It must read the logs, analyze the stack traces, and fix errors in-stream automatically.
- **Receipts**: Definitive proofs of success. E.g., `pytest` logs, Cryptographic Trace hashes, verified JSON outputs. SROS does not accept "Done" without a receipt.
- **Terminal Nullification**: A system state invoked by Plane 3 when safety policies are critically breached. All active sessions are forcefully purged, memory buffers flushed, and the OS drops back to Kernel standby.

---
> *Generated by Antigravity under Sovereign Directives.*
> *End of Document.*
