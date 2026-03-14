---
description: SR8 - Kernel Forge
---

<sr8_workflow
  id="SR8.SROS.KernelForge.Apex.Reforged"
  xmlns="https://sr8.sros/schema/v1"
  version="1.1.0"
  role="Kernel Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Kernel Forge Reforged</system_name>
    <purpose>
      Design and implement the SROS v1 Kernel Plane as the low level nervous
      system of SROS: Event Bus, Daemon Registry, Scheduler, Telemetry,
      Security, and Bootstrap, wired into Memory, Governance, and MirrorOS.
      The Kernel is the stable, deterministic backbone on which all other
      planes rest.
    </purpose>
  </identity>

  <context>
    <item>The Kernel is the only plane that must be 100 percent reliable.</item>
    <item>It owns process lifecycle, event streams, low level scheduling, and health.</item>
    <item>It must be model agnostic, side effect controlled, and replay friendly.</item>
    <item>It must expose clear contracts to Runtime, Governance, MirrorOS, and Adapters.</item>
  </context>

  <inputs>
    <item>Existing <code>sros/kernel/</code> directory structure and modules.</item>
    <item>Blueprint definitions for kernel daemons and plane responsibilities.</item>
    <item>Requirements from Runtime, Governance, MirrorOS, and Memory planes.</item>
  </inputs>

  <objectives>
    <item>Implement a deterministic Event Bus with typed topics and envelopes.</item>
    <item>Implement a Daemon Registry and lifecycle manager with dependency graph.</item>
    <item>Implement a Scheduler Daemon for cron, delayed, and recurring tasks.</item>
    <item>Implement core daemons: telemetry, memory, agent_router, security, heartbeat.</item>
    <item>Implement Kernel Bootstrap that wires config, memory, governance, MirrorOS.</item>
    <item>Define Kernel invariants, panic modes, and deadletter behavior.</item>
  </objectives>

  <workflow>
    <step order="1" id="event_bus_contract">
      Design <code>event_bus.py</code>:
      - EventEnvelope structure: id, timestamp, source_plane, component, topic, payload, correlation_id, tenant, severity.
      - Topic convention: <code>plane.component.action</code> with optional suffixes.
      - Synchronous in process dispatch with optional async hooks for later.
      - Subscription API: subscribe(topic_pattern, handler, options).
      - Deadletter handling for failed handlers and retry policies.
      - Instrumentation hooks for Governance and MirrorOS witness.
    </step>

    <step order="2" id="daemon_registry_contract">
      Design <code>daemon_registry.py</code>:
      - Daemon interface: <code>start()</code>, <code>stop()</code>, <code>health()</code>, <code>describe()</code>.
      - Dependency graph model: topological ordering, cycle detection at registration time.
      - Category tags: kernel_core, telemetry, security, adapter, experimental.
      - Health states: healthy, degraded, failing, stopped.
      - Restart policies: never, on_failure, always, limited_backoff.
      - Integration with event bus for lifecycle events like <code>kernel.daemon.started</code>.
    </step>

    <step order="3" id="scheduler_daemon_design">
      Design <code>daemons/scheduler_daemon.py</code>:
      - Task definition: id, callable_ref, schedule spec, retry policy, max_executions.
      - Simple cron like and interval schedules plus one shot delayed tasks.
      - Durable store option using Memory backend when configured.
      - Emission of <code>kernel.scheduler.tick</code> events for observability.
      - Backpressure controls and maximum concurrent tasks.
      - Safe shutdown semantics during Kernel stop.
    </step>

    <step order="4" id="core_daemons_design">
      Specify additional core daemons:
      - telemetry_daemon: aggregates metrics, forwards to MirrorOS trace_store.
      - memory_daemon: mediates access to Memory Router during boot and health checks.
      - agent_router_daemon: tracks active agents and runtime endpoints.
      - security_daemon: enforces low level safety checks, rate limits, and sandbox flags.
      - heartbeat_daemon: emits periodic <code>kernel.heartbeat</code> events per tenant.
      For each daemon define configuration keys, events published, health checks, and failure modes.
    </step>

    <step order="5" id="kernel_bootstrap_sequence">
      Design <code>kernel_bootstrap.py</code>:
      - <code>boot(config_path: str) -> KernelContext</code> that:
        * loads <code>sros_config.yml</code> and resolves environment overrides,
        * initializes logging and MirrorOS witness baseline,
        * creates core KernelState and EventBus,
        * registers core daemons with their dependencies,
        * initializes Memory Router and verifies connectivity,
        * links Governance policy_engine and MirrorOS witness to EventBus,
        * starts daemons in dependency order with health checks,
        * emits <code>kernel.ready</code> and returns a bound KernelContext.
      - <code>shutdown()</code> procedure with graceful stop and panic fallback.
    </step>

    <step order="6" id="kernel_state_and_context">
      Design <code>kernel_state.py</code> and <code>kernel_context.py</code>:
      - KernelState: immutable snapshot of active daemons, adapters, tenants, last heartbeat.
      - KernelContext: handle passed to other planes with access to EventBus, Memory, Governance, MirrorOS client.
      - Thread safe access patterns and read only views for non kernel code.
    </step>

    <step order="7" id="panic_and_replay_invariants">
      Define panic and replay rules:
      - Panic states for catastrophic failures with downgrade to safe mode.
      - Relationship between EventBus and MirrorOS trace_store to allow replay.
      - Requirements for idempotent event handlers in Kernel daemons.
      - How snapshot_manager can capture Kernel state at <code>kernel.ready</code>.
    </step>

    <step order="8" id="tests_and_examples">
      Define tests:
      - Unit tests for EventBus (subscription, ordering, failure, deadletter).
      - Unit tests for DaemonRegistry (dependencies, cycles, restart policies).
      - Unit tests for Scheduler (schedule parsing, retries, persistence).
      - Integration test: boot kernel with minimal config and assert heartbeat events.
      - Integration test: simulate failing daemon and verify restart and MirrorOS trace.
    </step>

    <step order="9" id="implementation_plan">
      Produce an implementation ordering:
      - EventBus and EventEnvelope,
      - KernelState and KernelContext,
      - DaemonRegistry,
      - core daemons,
      - Scheduler,
      - KernelBootstrap,
      - tests and example scripts.
      For each step, specify files to create and key functions.
    </step>
  </workflow>

  <checks>
    <item>The EventBus must never drop messages silently; failures go to deadletter with tracing.</item>
    <item>Daemon dependency cycles are detected at registration and refuse to boot.</item>
    <item>Kernel boot with minimal config must succeed in under one second excluding model warmup.</item>
    <item>Every core daemon emits health and lifecycle events observable by MirrorOS.</item>
    <item>Panic states and replay contracts are documented and testable.</item>
  </checks>

  <output_contract>
    <item>Narrative design of Kernel internals and invariants.</item>
    <item>File and function level implementation plan for all Kernel modules.</item>
    <item>Test plan with concrete test file names and example cases.</item>
    <item>Expected observable events in MirrorOS for a normal boot cycle.</item>
  </output_contract>

</sr8_workflow>
