---
description: SR8 Demo Producer
---

<sr8_workflow
  id="SR8.SROS.DemoShowcaseProducer.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Golden Demo Producer"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Demo Showcase Producer</system_name>
    <purpose>
      Design and orchestrate the Golden Demos for SROS v1 - polished, scripted
      scenarios such as Install Flow, Research Loop, Simulation Run, and Nexus
      Control Room that prove SROS is real, coherent, and sovereign. These
      demos must be reproducible, observable, and easy to run from CLI or Web.
    </purpose>
  </identity>

  <context>
    <item>Demos are marketing and validation at the same time.</item>
    <item>They must exercise real code paths, not mocked slideware.</item>
    <item>They should showcase all four planes, Governance, MirrorOS, and SRX agents.</item>
  </context>

  <inputs>
    <item>Existing demo scripts or tests, if any, under <code>examples/</code> or <code>tests/</code>.</item>
    <item>Nexus Core design from NexusCoreForge workflow.</item>
    <item>Simulation Harness, Agent Foundry, Memory and Codex designs.</item>
  </inputs>

  <objectives>
    <item>Define the list of Golden Demos for SROS v1.</item>
    <item>Design detailed scripts and required assets for each demo.</item>
    <item>Expose demos through CLI, HTTP, and Nexus UI.</item>
    <item>Ensure demos are telemetry rich and reproducible on fresh installs.</item>
  </objectives>

  <workflow>
    <step order="1" id="demo_catalog">
      Define demo catalog:
      - Install and First Boot - from empty system to <code>kernel.ready</code> with heartbeat and status dashboard.
      - Research Loop - SRX Researcher and Codex building a small knowledge pack and answering questions.
      - Self Orchestrated Build - Architect and Builder generating or refactoring a small module.
      - Simulation Storm - SimulationHarness running a stress scenario with visible telemetry.
      - Multi Tenant Split - two tenants using different adapters, policies, and codex packs in parallel.
      For each demo, assign a short id, title, and narrative goal.
    </step>

    <step order="2" id="demo_scripting">
      Outline scripts for each demo:
      - step by step actions (CLI commands or UI flows),
      - expected outputs at each step,
      - screenshots or recording anchors for future media.
      Ensure scripts can be followed without prior SROS knowledge.
    </step>

    <step order="3" id="demo_workflows">
      Model demos as SRXML workflows and Nexus commands:
      - each demo has an SRXML definition with stages and agents.
      - Nexus command <code>run_demo</code> accepts demo_id and options.
      - workflows emit structured events so MirrorOS can replay later.
      Provide example SRXML snippet for one demo.
    </step>

    <step order="4" id="demo_assets">
      Define assets:
      - sample datasets and codex packs,
      - config presets,
      - saved traces for replay segments.
      Specify where these live in the repo and how they are loaded by demos.
    </step>

    <step order="5" id="observability_and_recording">
      Ensure demos are observability showcases:
      - telemetry dashboards updated live during runs.
      - MirrorOS lenses showing flows across planes.
      - option to record a full trace for each demo run.
      Describe how to capture output for docs, videos, and investor decks.
    </step>

    <step order="6" id="cli_and_http_entrypoints">
      Design entrypoints:
      - CLI command <code>sros demo list</code>, <code>sros demo run --id</code>.
      - HTTP endpoint <code>/api/demos/run</code>.
      - simple Web page under Nexus with cards for each demo.
      Define parameters such as tenant, seed, and environment.
    </step>

    <step order="7" id="reproducibility_and_reset">
      Specify reset behavior:
      - isolated demo tenants and memory layers,
      - ability to reset system back to pre demo snapshot,
      - optional "dry run" mode for CI.
      Document expectations for running demos back to back without pollution.
    </step>

    <step order="8" id="tests_and_qc">
      Plan tests and quality checks:
      - automated tests that ensure demos still run after code changes.
      - snapshot tests for key outputs.
      - manual checklist for visual polish and narrative coherence.
    </step>
  </workflow>

  <checks>
    <item>Each Golden Demo must use real SROS pipelines end to end.</item>
    <item>Demos must be runnable on a fresh install with minimal prerequisites.</item>
    <item>Demos must leave the system in a clean and recoverable state.</item>
  </checks>

  <output_contract>
    <item>Golden Demo catalog and goals.</item>
    <item>Scripts, workflows, and assets required per demo.</item>
    <item>CLI, HTTP, and Nexus surfaces for running demos.</item>
    <item>Reproducibility, observability, and QC plan.</item>
  </output_contract>

</sr8_workflow>
