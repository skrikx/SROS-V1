---
description: SR8 - Self-Evolution Loop
---

<sr8_workflow
  id="SR8.SROS.SelfEvolutionLoop.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Self Evolution Loop Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Self Evolution Loop (Ouroboros)</system_name>
    <purpose>
      Design the controlled self evolution loop where SROS uses Architect and
      related agents to read its own code, telemetry, and MirrorOS traces,
      propose improvements, simulate changes, and emit human review packages.
      This loop must be powerful, sandboxed, and never auto deploy without
      explicit approval.
    </purpose>
  </identity>

  <context>
    <item>This is the most dangerous and powerful SROS workflow.</item>
    <item>It must be constrained by Governance, MirrorOS, and human review points.</item>
    <item>It primarily operates on code, config, tests, and docs of SROS itself.</item>
  </context>

  <inputs>
    <item>Architect, Builder, Tester, and Simulation Agents from AgentFoundry.</item>
    <item>MirrorOS traces, metrics, and drift detector outputs.</item>
    <item>Git repository or code storage for SROS source and tests.</item>
  </inputs>

  <objectives>
    <item>Define stages of the self evolution loop from observation to proposal.</item>
    <item>Integrate MirrorOS drift and incident data into improvement selection.</item>
    <item>Design safe sandboxes and simulation runs for proposed changes.</item>
    <item>Produce reviewable change bundles for humans, not auto apply patches.</item>
    <item>Ensure full auditability and rollback of the loop itself.</item>
  </objectives>

  <workflow>
    <step order="1" id="loop_stages">
      Define loop stages:
      - Observe: collect telemetry, traces, incidents, TODOs.
      - Analyze: Architect Agent synthesizes pain points and opportunities.
      - Propose: Architect and Builder draft design notes and code diffs.
      - Simulate: Simulation Agent runs tests and harness scenarios in sandbox.
      - Review: human or Governance gate evaluates proposals and results.
      - Record: MirrorOS logs the entire loop as a trace for later study.
      For each stage, specify responsible agents and required inputs.
    </step>

    <step order="2" id="scope_and_constraints">
      Define scope:
      - allowed targets: code, tests, docs, configs.
      - forbidden targets: secrets, production data, external systems.
      Constraints:
      - no changes are pushed to main branches without human approval.
      - loop must operate in a separate git branch or workspace.
      Describe how these constraints are enforced technically.
    </step>

    <step order="3" id="data_sources">
      Enumerate data sources:
      - MirrorOS drift_detector signals and high severity incidents.
      - Telemetry trends over time.
      - Open issues, TODOs, and FIXMEs in code.
      - manual feedback notes stored in codex.
      Design queries and lenses that feed these into Architect Agent.
    </step>

    <step order="4" id="proposal_generation">
      Specify how proposals are generated:
      - Architect writes a design brief per improvement item.
      - Builder generates patches, new modules, or refactors.
      - Tester writes or updates tests to cover changes.
      Use SRXML workflows to orchestrate agents and record design decisions.
    </step>

    <step order="5" id="simulation_and_validation">
      Define simulation phase:
      - run existing test suites in dedicated environment.
      - run SimulationHarness scenarios including stress and adversarial tests.
      - compare telemetry and performance vs baseline.
      Document metrics and thresholds required for a proposal to be considered viable.
    </step>

    <step order="6" id="review_and_approval">
      Design review mechanism:
      - produce a "Change Dossier" containing design notes, diffs, test results, metrics.
      - present this to human reviewers through CLI or Web UI.
      - allow Governance policies to encode additional gates (for example forbidding large refactors automatically).
      No change proceeds to merge without explicit acknowledgment.
    </step>

    <step order="7" id="recording_and_learning">
      Define how MirrorOS records loop runs:
      - tag traces with <code>loop.self_evolution</code> and proposal ids.
      - capture feedback from reviewers and final decisions.
      - allow the next loop iteration to learn from what was accepted or rejected.
    </step>

    <step order="8" id="fail_safes">
      Specify fail safes:
      - hard caps on number and size of concurrent proposals.
      - kill switches to disable loop on anomalies.
      - periodic audit of loop outcomes to detect bias or drift.
      Describe how operators can disable or throttle the loop via config.
    </step>
  </workflow>

  <checks>
    <item>No self evolution change is auto merged into production without human approval.</item>
    <item>All loop activities must be traceable and replayable in MirrorOS.</item>
    <item>Simulation results must show non regression at minimum before proposals are accepted.</item>
  </checks>

  <output_contract>
    <item>Stage by stage definition of the Self Evolution Loop.</item>
    <item>Agent orchestration and SRXML workflow design.</item>
    <item>Simulation, validation, and review criteria.</item>
    <item>Fail safes, governance gates, and auditability guarantees.</item>
  </output_contract>

</sr8_workflow>
