---
description: SR8 - SROS Test Suite Forge
---

<sr8_workflow
  id="SR8.SROS.TestSuiteForge.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Test Suite Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SROS Test Suite Forge</system_name>
    <purpose>
      Design a coherent, layered test strategy and concrete test files for
      SROS v1 so that kernel, runtime, governance, mirroros, adapters,
      Nexus Core, and SRXML are all covered by meaningful tests and demos.
    </purpose>
  </identity>

  <context>
    <item>The repo may currently have a small set of tests or none at all.</item>
    <item>We want tests that guard behavior and architecture, not fragile internals.</item>
    <item>Tests should be runnable locally without external secrets or services.</item>
  </context>

  <inputs>
    <item>tests/ directory contents, if any.</item>
    <item>Key entrypoints such as CLI commands and demo workflows.</item>
    <item>SRXML schemas and critical modules in each plane.</item>
  </inputs>

  <objectives>
    <item>Define test layers: unit, integration, cross plane, and demo level.</item>
    <item>Map each major module or plane to a set of required tests.</item>
    <item>Design naming and organization conventions for tests.</item>
    <item>Propose concrete test files and example test cases.</item>
  </objectives>

  <workflow>
    <step order="1" id="test_inventory">
      Inspect the current tests.
      Categorize them into:
      - unit tests,
      - integration tests,
      - end to end demos.
      Identify gaps where key modules or flows have no coverage.
    </step>

    <step order="2" id="test_layers_design">
      Define the four main layers of tests:
      - unit: single module functions and classes,
      - integration: multiple modules or a full plane,
      - cross_plane: flows that touch at least two planes,
      - demo: CLI or Nexus flows that represent real usage.
      For each layer, specify goals, tools, and structure.
    </step>

    <step order="3" id="plane_mapping">
      For each plane:
      - kernel,
      - runtime,
      - governance,
      - mirroros,
      map which tests are needed.
      Include SRXML, memory, codex, adapters, and Nexus as cross cutting concerns.
    </step>

    <step order="4" id="file_plan">
      Propose test file names and locations.
      For example:
      - tests/test_kernel_boot.py,
      - tests/test_srxml_parser.py,
      - tests/test_governance_policy_engine.py,
      - tests/test_mirroros_traces.py,
      - tests/test_nexus_scenario_demo.py.
      For each file, outline 3 to 5 specific test cases.
    </step>

    <step order="5" id="fixtures_and_helpers">
      Design reusable fixtures or helpers:
      - in memory backends for memory and codex,
      - stub model adapters,
      - sample SRXML documents,
      - stub policies and governance configs.
      Describe how they are implemented and shared across tests.
    </step>

    <step order="6" id="ci_strategy">
      Outline how tests should run in CI:
      - minimal test matrix,
      - fast default test suite,
      - optional slower or heavier tests,
      - reporting for coverage and regressions.
      Include guidelines for developers when adding new tests.
    </step>

    <step order="7" id="change_receipts">
      Suggest updates to README and docs:
      - how to run tests locally,
      - how to create new tests,
      - conventions for test naming and structure.
      Provide a concise checklist for future contributors.
    </step>
  </workflow>

  <checks>
    <item>Each plane must have at least one dedicated test file and cross plane tests.</item>
    <item>There must be at least one demo level test that calls the same code paths as manual demos.</item>
    <item>All tests must be runnable without external secrets by default.</item>
  </checks>

  <output_contract>
    <item>Provide a matrix of planes vs test layers showing coverage goals.</item>
    <item>List concrete test file names with bullet point test cases inside.</item>
    <item>Describe fixtures and helpers with suggested code signatures.</item>
    <item>End with CI recommendations and developer guidelines.</item>
  </output_contract>

</sr8_workflow>
