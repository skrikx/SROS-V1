---
description: SR8 - Nexus Core Forge
---

<sr8_workflow
  id="SR8.SROS.NexusCoreForge.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Nexus Core & Skrikx Interface Forge"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Nexus Core Forge</system_name>
    <purpose>
      Design and specify the Nexus Core for SROS v1, the Skrikx Prime
      interface that orchestrates SRX agents, workflows, memory and codex,
      governance, and MirrorOS, while exposing Gemini 3 abilities through
      model adapters in a controlled way.
    </purpose>
  </identity>

  <context>
    <item>Nexus Core is a programmable API and orchestration center, not a UI.</item>
    <item>It must be callable by CLI commands, HTTP routes, or external UIs.</item>
    <item>It must not be tightly coupled to any one model provider.</item>
  </context>

  <inputs>
    <item>Location for Nexus modules, for example <code>sros/apps/sros_web_nexus/</code>.</item>
    <item>SRX agents that Nexus will use: architect, research, builder, tester, simulation, memory curator.</item>
    <item>Gemini adapter and other model adapters.</item>
    <item>Existing demo workflows or flows planned in the blueprint.</item>
  </inputs>

  <objectives>
    <item>Define the responsibilities and boundaries of Nexus Core.</item>
    <item>Design the internal API for Nexus commands.</item>
    <item>Map Nexus commands to SRX agents and workflows.</item>
    <item>Ensure governance and MirrorOS are integrated into every Nexus path.</item>
    <item>Define one or more showcase scenarios that prove SROS v1 power.</item>
  </objectives>

  <workflow>
    <step order="1" id="role_definition">
      Describe what Nexus Core is and is not:
      - it is the central orchestrator for SROS usage,
      - it is not tied to one model or UI,
      - it is the canonical place where SROS business logic lives.
      Use this to anchor all subsequent design choices.
    </step>

    <step order="2" id="command_api_design">
      Design the main Nexus API entrypoints.
      For example:
      - run_nexus_command(command: str, payload: dict) → result,
      - list_capabilities() → list of commands and metadata,
      - get_session_status(session_id) → status.
      Define arguments, return types, and error handling.
    </step>

    <step order="3" id="command_catalog">
      Create a catalog of Nexus commands grouped by theme:
      - repo architecture and SROS building,
      - research and codex exploration,
      - simulation and governance testing,
      - MirrorOS inspection and replay,
      - creative or domain specific flows.
      For each command, map which SRX agents and workflows it will use.
    </step>

    <step order="4" id="adapter_integration">
      Describe how Nexus Core calls model adapters:
      - direct request to Gemini adapter for text and code,
      - use of tool calling when needed,
      - fallback to other adapters.
      Ensure calls flow through governance and MirrorOS instrumentation.
    </step>

    <step order="5" id="session_and_memory">
      Specify how Nexus manages sessions:
      - how session ids are created and stored,
      - how memory layers are attached to a session,
      - how codex packs are selected based on command context.
      Show how this ties into session_manager and memory_router.
    </step>

    <step order="6" id="governance_mirroros_integration">
      For each command type, define:
      - which policies must be checked before execution,
      - which witness and trace events are emitted,
      - how reflections or drift signals can be generated.
      Ensure that critical operations cannot bypass governance and MirrorOS.
    </step>

    <step order="7" id="showcase_scenarios">
      Design at least two showcase workflows:
      - one that uses Nexus to design or refactor part of SROS itself,
      - one that uses Nexus to run a complex research or simulation task.
      For each scenario, outline steps, agents, memory usage, governance checks,
      and MirrorOS observability.
    </step>

    <step order="8" id="tests_and_demos">
      Specify tests and demos:
      - unit tests for the Nexus API functions,
      - integration tests for at least one scenario,
      - CLI commands and HTTP routes that expose these scenarios.
      Suggest names and signatures for the main code files to implement.
    </step>
  </workflow>

  <checks>
    <item>Nexus Core must not depend directly on a single model provider.</item>
    <item>Every Nexus command must have a clear mapping to SRX agents or workflows.</item>
    <item>At least one scenario must run through all four planes and both governance and MirrorOS.</item>
  </checks>

  <output_contract>
    <item>Provide a narrative design for Nexus Core first.</item>
    <item>Provide a table mapping commands to agents, workflows, and planes.</item>
    <item>Provide suggested function signatures and module layout for Nexus.</item>
    <item>End with a stepwise implementation plan that can be followed in this workspace.</item>
  </output_contract>

</sr8_workflow>
