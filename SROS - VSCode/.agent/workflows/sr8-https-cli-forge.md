---
description: SR8 - HTTP and CLI Surface Forge
---

<sr8_workflow
  id="SR8.SROS.HTTP_and_CLI_SurfaceForge.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="HTTP + CLI Surface Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - HTTP and CLI Surface Forge</system_name>
    <purpose>
      Design and specify the HTTP API and CLI surfaces for SROS v1 so that
      kernel, runtime, governance, mirroros, and Nexus can be operated from
      both command line and web frontends in a consistent, discoverable way.
    </purpose>
  </identity>

  <context>
    <item>SROS will be used by developers, operators, and potentially clients.</item>
    <item>HTTP and CLI are the first public surfaces for interacting with SROS.</item>
    <item>They must be minimal yet expressive, and tightly governed.</item>
  </context>

  <inputs>
    <item>Existing CLI modules under <code>sros/cli/</code>.</item>
    <item>Existing HTTP server or plans under <code>sros/apps/</code> or <code>sros/api/</code>.</item>
    <item>Known demos and workflows from the blueprint.</item>
  </inputs>

  <objectives>
    <item>Define a clear set of CLI commands for core tasks.</item>
    <item>Define HTTP endpoints that expose key flows safely.</item>
    <item>Ensure both surfaces follow the same mental model and naming.</item>
    <item>Specify authentication, authorization, and observability expectations.</item>
  </objectives>

  <workflow>
    <step order="1" id="user_roles">
      Identify user personas for these surfaces:
      - SROS developer,
      - SROS operator,
      - power user or architect,
      - automated systems or CI.
      For each persona, define typical tasks and workflows.
    </step>

    <step order="2" id="cli_commands_design">
      Propose CLI commands grouped by function:
      - initialization and configuration,
      - running demos and simulations,
      - inspecting state, memory, and MirrorOS traces,
      - managing codex packs and policies,
      - diagnostics and health checks.
      For each command, specify:
      - name and subcommands,
      - arguments and flags,
      - expected output shape.
    </step>

    <step order="3" id="http_endpoints_design">
      Design HTTP endpoints grouped by resource:
      - /health, /info,
      - /demo, /workflow,
      - /nexus, /sessions,
      - /mirror, /governance.
      For each endpoint, specify:
      - HTTP method and path,
      - request body schema,
      - response schema,
      - authentication requirements.
    </step>

    <step order="4" id="cross_surface_consistency">
      Ensure that CLI and HTTP reflect the same concepts.
      Map CLI commands to HTTP endpoints or flows.
      Use consistent terminology for sessions, workflows, demos, and Nexus commands.
    </step>

    <step order="5" id="governance_integration">
      Define how governance controls access:
      - mapping between roles and commands/endpoints,
      - policies that must be checked before execution,
      - audit logging requirements for sensitive operations.
      Provide examples of policy rules that match CLI or HTTP actions.
    </step>

    <step order="6" id="mirroros_integration">
      Specify how MirrorOS observes surface usage:
      - events emitted for commands and requests,
      - trace identifiers and correlation ids,
      - lenses that summarize recent surface activity.
      Outline how operators can query MirrorOS for surface level insights.
    </step>

    <step order="7" id="documentation_and_examples">
      Propose documentation structure:
      - quickstart examples for CLI and HTTP,
      - detailed reference for each command and endpoint,
      - sample scripts or curl commands.
      Describe one or two full walkthroughs using these surfaces.
    </step>
  </workflow>

  <checks>
    <item>Every core SROS capability must be reachable from at least one surface.</item>
    <item>No endpoint or command may bypass governance or MirrorOS instrumentation.</item>
    <item>Surface design must avoid exposing low level internal details unnecessarily.</item>
  </checks>

  <output_contract>
    <item>Provide CLI and HTTP design tables.</item>
    <item>Provide sample command invocations and HTTP requests.</item>
    <item>Provide notes on auth, governance, and MirrorOS hooks.</item>
    <item>End with a list of files or modules to create or extend for implementation.</item>
  </output_contract>

</sr8_workflow>
