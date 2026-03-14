---
description: SR8 - Memory and Codex Fabric
---

<sr8_workflow
  id="SR8.SROS.MemoryCodexFabric.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Memory & Codex Fabric Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Memory and Codex Fabric</system_name>
    <purpose>
      Design and specify the SROS v1 memory and codex fabric: backends,
      layers, routing, and codex packs that will support agents, workflows,
      MirrorOS, and Nexus Core in a consistent and extensible way.
    </purpose>
  </identity>

  <context>
    <item>The blueprint defines multiple backends and layers for memory and codex.</item>
    <item>Agents expect a unified API to read and write without caring about storage details.</item>
    <item>MirrorOS and governance require reliable access to logs and history.</item>
    <item>The repo may have partial implementations or none at all.</item>
  </context>

  <inputs>
    <item>Directories such as <code>sros/memory/</code> and <code>sros/codex/</code>.</item>
    <item>Any existing backends: sqlite, vector, file, in memory.</item>
    <item>Any written notes about codex packs for core, research, or playbooks.</item>
  </inputs>

  <objectives>
    <item>Define the canonical memory API: functions, data types, and error model.</item>
    <item>Map out layers (short term, long term, codex, analytics) and how they stack.</item>
    <item>Design the configuration model for backends and routing.</item>
    <item>Specify codex pack structure and how agents use it.</item>
    <item>Propose tests and demos that prove the fabric works.</item>
  </objectives>

  <workflow>
    <step order="1" id="use_cases">
      List the main use cases for memory and codex in SROS v1:
      - conversational state for agents,
      - long term knowledge and config,
      - SRXML and prompt history,
      - MirrorOS traces and snapshots,
      - codex packs for research and playbooks.
      Use these to ground your later design.
    </step>

    <step order="2" id="api_design">
      Define the core memory API from an agent perspective.
      For example:
      - get(key, layer, options),
      - set(key, value, layer, options),
      - search(query, layer, options),
      - list(prefix, layer).
      Describe arguments, return types, and possible errors.
    </step>

    <step order="3" id="layer_model">
      Describe each layer:
      - short_term_layer,
      - long_term_layer,
      - codex_layer,
      - analytics_layer.
      For each layer, specify:
      - what data it stores,
      - expected volume and access patterns,
      - retention and eviction strategy,
      - which backends it might use.
    </step>

    <step order="4" id="backend_mapping">
      For each backend (sqlite, file, vector, in memory, postgres, cloud store):
      - list its strengths and weaknesses,
      - propose default usage in dev and prod,
      - define configuration keys (paths, connection strings, limits).
      Explain how memory_config will express these choices.
    </step>

    <step order="5" id="router_design">
      Design memory_router behavior:
      - how it resolves a request to a layer and backend,
      - how to support pluggable routing strategies,
      - how to instrument calls with governance and MirrorOS telemetry.
      Provide pseudocode or function signatures.
    </step>

    <step order="6" id="codex_structure">
      Define codex_index, codex_loader, and codex_search responsibilities.
      Specify how codex packs are laid out on disk:
      - folder naming,
      - metadata files,
      - index format,
      - content format.
      Provide at least one concrete example pack layout.
    </step>

    <step order="7" id="tests_demos">
      Propose a set of unit and integration tests:
      - API level tests for memory and codex,
      - routing tests,
      - simple end to end tests where an agent writes to memory and retrieves it later,
      - a demo that shows codex search powering an SRX research agent.
    </step>
  </workflow>

  <checks>
    <item>The memory API must be simple enough for agents to use without boilerplate.</item>
    <item>At least one configuration path must support purely local development with no external services.</item>
    <item>Codex packs must be easy to ship inside the repo and update over time.</item>
  </checks>

  <output_contract>
    <item>Produce a narrative design first.</item>
    <item>Then provide tables that map layers to backends and config keys.</item>
    <item>Then provide example function signatures and pseudo code for router and codex modules.</item>
    <item>End with a checklist of code files to create or update to realize this design.</item>
  </output_contract>

</sr8_workflow>
