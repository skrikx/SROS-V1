---
description: SR8 - SROS Safe Refactor & Cleanup
---

<sr8_workflow
  id="SR8.SROS.RepoRefactor.SafeGuard.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Safe Refactor Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SROS Safe Refactor & Cleanup</system_name>
    <purpose>
      Analyze the existing SROS repo, identify messy or duplicated areas,
      and design safe refactors that improve clarity and modularity without
      breaking core flows or diverging from the SROS v1 blueprint.
    </purpose>
  </identity>

  <context>
    <item>This workflow assumes the repo already exists with partial implementations.</item>
    <item>Some modules may have grown organically during early experiments.</item>
    <item>The blueprint is the source of truth for the target architecture.</item>
    <item>Refactors must preserve behavior except where intentional improvements are made.</item>
  </context>

  <inputs>
    <item>Repo root path and current tree listing.</item>
    <item>Recent design decisions from docs/FINISH_NOTES or BUILD_LOG if present.</item>
    <item>Knowledge of key entrypoints: CLI, HTTP API, demos, Nexus Core.</item>
  </inputs>

  <objectives>
    <item>Identify hot spots: tangled modules, duplicate logic, unclear boundaries.</item>
    <item>Propose refactors that move code toward the four plane model and blueprint structure.</item>
    <item>Classify refactors by risk level and dependency impact.</item>
    <item>Define migration steps and guardrails, including tests to write first.</item>
  </objectives>

  <workflow>
    <step order="1" id="hotspot_scan">
      Inspect the repo structure and code.
      Look for:
      - mixed concerns in single modules,
      - circular imports,
      - ad hoc utilities that should live in common layers,
      - duplicated patterns across planes.
      Summarize top candidates in a table with rough risk scores.
    </step>

    <step order="2" id="blueprint_alignment">
      For each hotspot, compare its current role with the blueprint expectations.
      Decide whether the module:
      - belongs in a different plane,
      - should be split into multiple modules,
      - should be merged with an existing canonical module,
      - or should be deprecated slowly.
      Record decisions with justification tied to blueprint sections.
    </step>

    <step order="3" id="refactor_design">
      Design concrete refactor plans.
      For each plan, define:
      - name and short description,
      - files involved,
      - dependency impacts,
      - expected behavioral changes (if any),
      - new structure after refactor.
      Prioritize small, reversible steps over massive rewrites.
    </step>

    <step order="4" id="guardrails">
      Define guardrails for safe refactors:
      - tests that must exist or be written before applying changes,
      - checks for import loops or broken interfaces,
      - logging or MirrorOS traces to confirm behavior is preserved.
      Propose specific test cases for each major refactor.
    </step>

    <step order="5" id="migration_path">
      Create a migration sequence:
      - low risk refactors first,
      - high risk refactors blocked behind tests,
      - clear stopping points where the repo remains functional.
      Each step should be representable as a commit with a meaningful message.
    </step>

    <step order="6" id="change_receipts">
      Draft entries for FINISH_NOTES or BUILD_LOG:
      - which modules are being refactored,
      - which responsibilities are moving and why,
      - which invariants must hold after each step.
      This allows future you to see the logic behind structural changes.
    </step>
  </workflow>

  <checks>
    <item>Every proposed refactor must have an associated test or verification strategy.</item>
    <item>No refactor plan may leave the repo in a non bootable state without a clear recovery path.</item>
    <item>Blueprint alignment must be explicit, not assumed.</item>
  </checks>

  <output_contract>
    <item>Produce a ranked list of refactor opportunities with risk and impact.</item>
    <item>Provide a detailed refactor plan for the top 3 to 5 hotspots.</item>
    <item>Include a test and guardrail plan that can be executed before code changes.</item>
    <item>End with a proposed commit sequence and commit message outlines.</item>
  </output_contract>

</sr8_workflow>
