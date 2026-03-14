---
description: SR8 - SROS Developer Onboarding Forge
---

<sr8_workflow
  id="SR8.SROS.DevOnboardingDocs.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Developer Onboarding Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SROS Developer Onboarding Forge</system_name>
    <purpose>
      Design a complete onboarding documentation and learning path for new
      engineers joining the SROS project so they can understand the planes,
      core modules, workflows, and contribution rules without hand holding.
    </purpose>
  </identity>

  <context>
    <item>SROS is complex and deeply architectural.</item>
    <item>New contributors need a scaffold to become productive without breaking invariants.</item>
    <item>Docs must be in repo and tied to the blueprint and code.</item>
  </context>

  <inputs>
    <item>Existing docs/ directory and README.</item>
    <item>SROS_v1_Blueprint and any FINISH_NOTES or BUILD_LOG.</item>
    <item>List of common developer tasks and commands.</item>
  </inputs>

  <objectives>
    <item>Define an onboarding path for the first day, week, and month.</item>
    <item>Design documentation artifacts and their locations.</item>
    <item>Create checklists and exercises that force real understanding.</item>
    <item>Encode contribution rules tied to governance and MirrorOS.</item>
  </objectives>

  <workflow>
    <step order="1" id="audience_definition">
      Describe the target developer profile:
      - experience level,
      - languages known,
      - familiarity with AI and agents.
      Use this to calibrate depth and tone of docs.
    </step>

    <step order="2" id="day_one_path">
      Design a day one path:
      - clone repo,
      - install dependencies,
      - run quick demo,
      - open key files in each plane,
      - read blueprint summary.
      Provide explicit commands and file paths.
    </step>

    <step order="3" id="week_one_path">
      Design a week one path:
      - read deeper docs on planes and SRXML,
      - run tests and study failures if any,
      - implement or fix one small issue guided by docs,
      - introspect MirrorOS traces from a demo run.
      Specify which docs and modules they should focus on.
    </step>

    <step order="4" id="month_one_path">
      Design a month one path:
      - own a small feature or refactor,
      - write or improve tests,
      - propose a design change and document it,
      - run at least one governance or MirrorOS experiment.
      Include acceptance criteria for "onboarded".
    </step>

    <step order="5" id="documentation_structure">
      Propose documentation files and structure:
      - docs/overview.md,
      - docs/planes.md,
      - docs/srxml_guide.md,
      - docs/developer_onboarding.md,
      - docs/contribution_guide.md,
      - docs/mirroros_and_governance.md.
      For each, outline sections and expected content.
    </step>

    <step order="6" id="exercises_and_checks">
      Design small exercises:
      - follow a trace through planes,
      - add a new SRXML workflow template,
      - write a new test case,
      - observe governance decisions in logs.
      Suggest how mentors can check their outcomes.
    </step>

    <step order="7" id="contribution_rules">
      Encode rules for contributions:
      - coding style,
      - test requirements,
      - documentation updates,
      - governance and MirrorOS considerations.
      Show how these rules tie into PR templates or CI checks.
    </step>
  </workflow>

  <checks>
    <item>The onboarding path must be realistic for a single engineer.</item>
    <item>Docs must live inside the repo, not external tools.</item>
    <item>Every onboarding step should strengthen understanding of SROS principles, not just mechanics.</item>
  </checks>

  <output_contract>
    <item>Provide a narrative onboarding story for day one, week one, month one.</item>
    <item>Provide a proposed docs file tree and section outlines.</item>
    <item>Provide sample exercises and verification steps.</item>
    <item>End with a contribution checklist suitable for a README or CONTRIBUTING file.</item>
  </output_contract>

</sr8_workflow>
