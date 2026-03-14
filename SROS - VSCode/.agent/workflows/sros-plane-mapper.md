---
description: Scan the current SROS repository and map every directory and module       to the four SROS planes and the core support layers, then design a concrete evolution plan that aligns the repo to the SROS v1 blueprint.
---

<sr8_workflow
  id="SR8.SROS.PlaneMapper.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="SROS Plane Mapper"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SROS Plane & Module Mapper</system_name>
    <purpose>
      Scan the current SROS repository and map every directory and module
      to the four SROS planes and the core support layers, then design a
      concrete evolution plan that aligns the repo to the SROS v1 blueprint.
    </purpose>
  </identity>

  <context>
    <item>This workflow runs inside the SROS repo design workspace.</item>
    <item>The SROS_v1_Blueprint.md file contains the authoritative architecture.</item>
    <item>The repo structure may be partially implemented, inconsistent, or empty.</item>
    <item>Your task is to bring order without breaking the SROS vision.</item>
  </context>

  <inputs>
    <item>Path to repo root, for example: <code>sros_v1/</code>.</item>
    <item>Path to SROS blueprint file: <code>docs/SROS_v1_Blueprint.md</code> or equivalent.</item>
    <item>Current directory and module listing from the workspace file explorer.</item>
  </inputs>

  <objectives>
    <item>Map every top level directory to kernel, runtime, governance, mirroros, or support layers.</item>
    <item>Map every Python package and major module to an explicit plane responsibility.</item>
    <item>Identify missing modules required by the blueprint.</item>
    <item>Identify conflicting or redundant modules that should be merged or removed later.</item>
    <item>Produce a written evolution plan that can be followed across multiple sessions.</item>
  </objectives>

  <workflow>
    <step order="1" id="scan_blueprint">
      Read the SROS_v1_Blueprint file and extract:
      - list of planes and their responsibilities,
      - list of required module groups and directories,
      - any existing diagrams or mappings.
      Summarize this in a short table for yourself in the answer.
    </step>

    <step order="2" id="scan_repo">
      List the repo tree starting at the configured root.
      Group paths into:
      - kernel candidates,
      - runtime candidates,
      - governance candidates,
      - mirroros candidates,
      - SRXML core,
      - memory and codex,
      - adapters,
      - cli and apps,
      - unknown or misc.
    </step>

    <step order="3" id="plane_assignment">
      For each directory and key module:
      - assign one primary plane,
      - note any secondary cross plane dependencies,
      - flag anything that sits outside the four plane model.
      Output this as a markdown table in the answer.
    </step>

    <step order="4" id="gap_analysis">
      Compare the blueprint list with the repo list.
      Identify:
      - missing directories and modules,
      - modules that exist but have unclear roles,
      - modules whose names conflict with blueprint naming.
      For each gap, explain:
      - what is missing,
      - why it matters,
      - which plane it belongs to.
    </step>

    <step order="5" id="evolution_plan">
      Design a concrete evolution plan made of ordered milestones.
      Each milestone must have:
      - name and short description,
      - plane focus,
      - target files and directories,
      - expected intermediate demos or tests.
      Ensure there is at least one demo that exercises:
      kernel → runtime → governance → mirroros.
    </step>

    <step order="6" id="change_receipts">
      Propose entries for a BUILD_LOG or FINISH_NOTES file documenting:
      - the current mapping snapshot,
      - the next three actions to take in code,
      - any modules to avoid touching until later.
    </step>
  </workflow>

  <checks>
    <item>Every directory and package must be assigned to a plane or support layer.</item>
    <item>No blueprint module group is left unmentioned.</item>
    <item>At least one end to end flow is identified and tagged for later implementation.</item>
  </checks>

  <output_contract>
    <item>Start with a short summary of how aligned the repo is right now.</item>
    <item>Include a markdown table mapping modules to planes.</item>
    <item>Include a numbered list of gaps with explanations.</item>
    <item>Include a milestone style evolution plan that can be executed in phases.</item>
    <item>End with a concise list called "Next three commits" with very concrete actions.</item>
  </output_contract>

</sr8_workflow>