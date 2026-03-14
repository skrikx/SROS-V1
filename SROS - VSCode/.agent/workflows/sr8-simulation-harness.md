---
description: SR8 - Simulation Harness
---

<sr8_workflow
  id="SR8.SROS.SimulationHarness.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Simulation Harness Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Simulation Harness</system_name>
    <purpose>
      Design the SROS v1 simulation harness in the Runtime plane: deterministic,
      reproducible scenarios that exercise Kernel, Runtime, Governance, and
      MirrorOS under failure, high load, and adversarial input conditions.
    </purpose>
  </identity>

  <context>
    <item>Simulations live under <code>sros/runtime/simulations/</code> and use MirrorOS traces and SRXML workflows.</item>
    <item>They must be safe to run without harming real data or external systems.</item>
    <item>They are key to proving SROS sovereignty and robustness.</item>
  </context>

  <inputs>
    <item>Existing <code>simulation</code> modules or stubs, if any.</item>
    <item>MirrorOS trace_store and replay_engine designs.</item>
    <item>Kernel and Runtime entrypoints for starting workflows and agents.</item>
  </inputs>

  <objectives>
    <item>Define the simulation API and scenario model.</item>
    <item>Design a catalog of scenarios: load, failure, adversarial, governance checks.</item>
    <item>Integrate simulations with MirrorOS replay and snapshots.</item>
    <item>Expose simulations via CLI and Nexus for interactive use.</item>
  </objectives>

  <workflow>
    <step order="1" id="simulation_model">
      Define the simulation model:
      - SimulationScenario object with id, name, description, category, parameters, expected outcomes.
      - Categories: load_test, failure_injection, adversarial_input, governance_policy_test, replay_debug.
      - Configuration via SRXML or YAML definitions.
    </step>

    <step order="2" id="simulation_api">
      Design <code>simulation_harness.py</code>:
      - <code>run_scenario(scenario_id, params)</code>,
      - <code>list_scenarios()</code>,
      - <code>describe_scenario(scenario_id)</code>.
      Define how scenarios are registered and discovered at runtime.
    </step>

    <step order="3" id="scenario_catalog">
      Define key scenarios:
      - Kernel stress test with many events and tasks.
      - Adapter failure injection where model or storage calls fail randomly.
      - Governance strict mode where risky actions are denied.
      - Adversarial prompt injection test for agents.
      - MirrorOS replay of past production like traces in sandbox.
      For each scenario, specify inputs, steps, and success metrics.
    </step>

    <step order="4" id="mirroros_integration">
      Specify how simulations interact with MirrorOS:
      - reuse trace_store and replay_engine for replay scenarios,
      - record simulation tags and scenario ids in traces,
      - allow comparisons of behavior between baseline and current version.
    </step>

    <step order="5" id="safety_guards">
      Define safety rules:
      - simulations run in a sandboxed tenant or environment,
      - external calls are mocked or limited,
      - state writes are discarded or isolated.
      Document how this is enforced through config and Governance policies.
    </step>

    <step order="6" id="cli_nexus_exposure">
      Design CLI and Nexus entrypoints:
      - CLI command <code>sros run-simulation --id</code>,
      - Nexus command <code>run_simulation</code> with scenario metadata,
      - outputs that show metrics, failures, and traces.
    </step>

    <step order="7" id="tests_and_regressions">
      Plan tests:
      - unit tests for simulation harness API,
      - simple scenarios that validate harness wiring,
      - regression tests that replay known bugs and verify they are fixed,
      - performance baseline tests for load scenarios.
    </step>
  </workflow>

  <checks>
    <item>Simulations must be reproducible given the same configuration and seeds.</item>
    <item>No simulation may mutate production state or bypass Governance and MirrorOS.</item>
    <item>At least one scenario must exercise all four planes together.</item>
  </checks>

  <output_contract>
    <item>Simulation model and API design.</item>
    <item>Scenario catalog with detailed descriptions.</item>
    <item>Safety and sandboxing guidelines.</item>
    <item>CLI and Nexus exposure plan plus tests.</item>
  </output_contract>

</sr8_workflow>
