---
description: SR8 - Demo Showcase Producer
---

<sr8_workflow
  id="SR8.SROS.DemoShowcase.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Showcase Producer"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Demo Showcase Producer</system_name>
    <purpose>
      Design and polish the "Golden Demos" that showcase SROS v1 capabilities.
      These are end-to-end narratives that prove the system is alive,
      sovereign, and powerful.
    </purpose>
  </identity>

  <context>
    <item>Demos are the primary way to communicate value.</item>
    <item>They must be reliable, visually impressive (CLI/Web), and self-contained.</item>
  </context>

  <inputs>
    <item>All SROS capabilities (Kernel, Runtime, Nexus).</item>
    <item>Specific user stories (The Researcher, The Builder).</item>
  </inputs>

  <objectives>
    <item>Produce the "Hello SROS" Demo (Boot + Chat).</item>
    <item>Produce the "Research Loop" Demo (Agent + Tools + Codex).</item>
    <item>Produce the "Self-Healing" Demo (Simulation + Governance).</item>
    <item>Produce the "Nexus Dashboard" Demo (Real-time Telemetry).</item>
  </objectives>

  <workflow>
    <step order="1" id="hello_sros_demo">
      Script:
      - Boot Kernel (show logs).
      - User: "Who are you?"
      - Agent: "I am SROS v1..."
      - Show Memory persistence (restart and ask "What did I just ask?").
    </step>

    <step order="2" id="research_loop_demo">
      Script:
      - User: "Research the history of SROS."
      - Agent: Plans -> Searches Codex -> Browses Web -> Writes Report.
      - Show the artifact being saved to disk.
    </step>

    <step order="3" id="self_healing_demo">
      Script:
      - Inject a failure (kill a daemon).
      - Show Kernel detecting it and restarting it.
      - Show MirrorOS logging the event.
    </step>

    <step order="4" id="packaging">
      Create `sros/apps/demos/` scripts:
      - `run_hello.py`
      - `run_research.py`
      - Ensure they have nice CLI output (spinners, colors).
    </step>
  </workflow>

  <checks>
    <item>Demos must run on a fresh install.</item>
    <item>Demos must clean up after themselves.</item>
  </checks>

  <output_contract>
    <item>Python scripts for each demo.</item>
    <item>A `demo_guide.md` walkthrough.</item>
    <item>Video recording scripts (optional).</item>
  </output_contract>

</sr8_workflow>
