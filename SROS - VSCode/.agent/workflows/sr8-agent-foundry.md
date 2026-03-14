---
description: SR8 - Agent Foundry
---

<sr8_workflow
  id="SR8.SROS.AgentFoundry.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="SRX Agent Foundry"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SRX Agent Foundry</system_name>
    <purpose>
      Create a factory and pattern library for SRX agents in SROS v1:
      the base class, lifecycle, and persona specific agents such as
      Architect, Researcher, Builder, Tester, and Simulation agents.
      Agents are the citizens of SROS and must be born through a
      standardized, governed process.
    </purpose>
  </identity>

  <context>
    <item>Agents live primarily in the Runtime plane under <code>sros/runtime/agents/</code>.</item>
    <item>They depend on Kernel context, Memory, Codex, Adapters, Governance, and MirrorOS.</item>
    <item>Agent creation must be repeatable and SRXML describable.</item>
  </context>

  <inputs>
    <item>Existing <code>srx_base_agent.py</code> or equivalent, if present.</item>
    <item>SROS v1 blueprint descriptions of key SRX personas.</item>
    <item>SRXML agent prompt schemas and templates.</item>
  </inputs>

  <objectives>
    <item>Define the SRXBaseAgent interface and lifecycle.</item>
    <item>Design an AgentFactory for instantiating agents by id and persona.</item>
    <item>Define canonical SRX personas: Architect, Researcher, Builder, Tester, Simulation, MemoryCurator.</item>
    <item>Bind agents to SRXML definitions and Governance policies.</item>
    <item>Create tests and demos that show agents cooperating in workflows.</item>
  </objectives>

  <workflow>
    <step order="1" id="base_agent_contract">
      Design <code>srx_base_agent.py</code>:
      - core methods: <code>plan()</code>, <code>act()</code>, <code>reflect()</code>, <code>run()</code>,
      - attributes: id, name, persona, capabilities, default_tools, default_memory_layers,
      - dependency injection for context, adapters, and MirrorOS client,
      - hooks for Governance checks before actions and MirrorOS witness during execution.
    </step>

    <step order="2" id="agent_lifecycle">
      Describe agent lifecycle:
      - initialization from SRXML or config,
      - session binding and memory hydration,
      - execution loop for single task vs multi step workflow,
      - reflection and self evaluation at the end of runs,
      - termination semantics and cleanup.
      Define events emitted at each stage via EventBus.
    </step>

    <step order="3" id="agent_factory_design">
      Design <code>agent_factory.py</code> or registry:
      - mapping from agent_id or persona to implementation class,
      - configuration of default model adapters and tools per persona,
      - ability to register new custom agents at runtime,
      - integration with Governance for allowed agent types per tenant.
    </step>

    <step order="4" id="persona_definitions">
      Specify canonical personas:
      - Architect Agent: designs and modifies SROS and systems.
      - Researcher Agent: performs deep research and codex operations.
      - Builder Agent: generates and edits code and configuration.
      - Tester Agent: writes and runs tests, evaluates outputs.
      - Simulation Agent: runs what if and replay scenarios using MirrorOS traces.
      - MemoryCurator Agent: organizes and prunes memory and codex.
      For each persona define goals, capabilities, default tools, and risks.
    </step>

    <step order="5" id="srxml_integration">
      Define how SRXML describes agents:
      - required fields (id, role, tenant, runtime, locks),
      - capabilities and constraints,
      - default workflows or contexts.
      Ensure SRXML agent definitions can be loaded and instantiated via AgentFactory.
    </step>

    <step order="6" id="governance_policies">
      Link agents to Governance:
      - policy rules per persona for allowed tools and adapters,
      - risk levels and thresholds,
      - evaluation templates for agent output quality.
      Provide policy examples for Architect vs Researcher vs Simulation.
    </step>

    <step order="7" id="mirroros_observability">
      Define MirrorOS hooks:
      - witness entries for agent start, actions, and reflections,
      - lenses for per agent performance and drift analysis,
      - trace linkage between agent runs and Kernel events.
    </step>

    <step order="8" id="tests_and_demos">
      Plan tests and demos:
      - unit tests for base agent lifecycle,
      - tests for AgentFactory instantiation from SRXML,
      - integration demo of Architect + Builder + Tester working on a small change,
      - MirrorOS backed simulation demo using Simulation Agent and a trace.
    </step>
  </workflow>

  <checks>
    <item>All SRX agents must derive from a single base class or protocol.</item>
    <item>New agents must be creatable solely via SRXML and configuration, no hard coding.</item>
    <item>Agent actions must be observable and governable.</item>
  </checks>

  <output_contract>
    <item>Base agent contract and lifecycle description.</item>
    <item>Design for AgentFactory and registration process.</item>
    <item>Definitions for canonical SRX personas and their policies.</item>
    <item>Demos and tests proving the agent foundry works.</item>
  </output_contract>

</sr8_workflow>
