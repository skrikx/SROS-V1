---
description: SR8 - SRXML Core Forge
---

<sr8_workflow
  id="SR8.SROS.SRXMLCoreForge.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="SRXML Core & Schema Forger"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SRXML Core Forge</system_name>
    <purpose>
      Design and implement the SRXML core for SROS v1: parser, validator,
      schemas, and templates for agents, workflows, and policies, aligned
      tightly with how the runtime and governance planes will actually use them.
    </purpose>
  </identity>

  <context>
    <item>SRXML is the canonical language for SROS prompts, workflows, and policies.</item>
    <item>The blueprint defines required schema families: agent, workflow, policy.</item>
    <item>The current repo may have partial or stub SRXML files.</item>
    <item>This workflow focuses on design and specification, not just code generation.</item>
  </context>

  <inputs>
    <item>Existing SRXML directory, if present: <code>sros/srxml/</code>.</item>
    <item>Any current schemas such as <code>base_srxml_schema.xml</code>.</item>
    <item>SROS blueprint sections that talk about SRXML structure and agents.</item>
    <item>Knowledge of how runtime and governance modules will consume SRXML.</item>
  </inputs>

  <objectives>
    <item>Define a clear conceptual model for SRXML documents in SROS v1.</item>
    <item>Specify the minimal but powerful fields required for agents, workflows, and policies.</item>
    <item>Design schemas that can be validated both syntactically and semantically.</item>
    <item>Create human friendly templates that engineers can fill without guesswork.</item>
    <item>Outline how SRXML will evolve for future SROS versions.</item>
  </objectives>

  <workflow>
    <step order="1" id="concept_model">
      Describe the conceptual model of SRXML in this repo:
      - what an agent document is,
      - what a workflow document is,
      - what a policy document is,
      - how they reference each other.
      Map this model to concrete Python structures that will live in the runtime and governance planes.
    </step>

    <step order="2" id="schema_inventory">
      Inspect any existing SRXML schemas or files.
      For each file, note:
      - document type,
      - key elements and attributes,
      - any obvious inconsistencies with the blueprint.
      Summarize findings in the answer.
    </step>

    <step order="3" id="schema_design">
      Design three primary XSD or XML schema files:
      - base_srxml_schema,
      - agent_prompt_schema,
      - workflow_schema,
      - policy_schema.
      For each, list the required elements, attributes, and relationships.
      Ensure they include fields for ids, roles, tenants, runtime, locks,
      objectives, inputs, execution plan, and success criteria.
    </step>

    <step order="4" id="template_design">
      Design SRXML templates that correspond to the schemas:
      - one for SRX agents like the Repo Architect,
      - one for workflows like Plane Mapper or Nexus Forge,
      - one for governance policies.
      Write them in a way that can be pasted and filled by humans.
    </step>

    <step order="5" id="parser_validator_contract">
      Define how the parser and validator should behave:
      - input types and formats,
      - error reporting style,
      - strictness levels,
      - mapping from XML to Python objects.
      Propose function signatures and module layout for parser and validator modules.
    </step>

    <step order="6" id="integration_points">
      Identify all places in the repo that will depend on SRXML:
      - runtime workflow engine,
      - SRX agents that use SRXML prompts,
      - governance policies,
      - tests and demos.
      For each integration point, describe how SRXML is passed in and what is returned.
    </step>

    <step order="7" id="evolution_notes">
      Suggest how SRXML could evolve in future SROS versions:
      - extension mechanisms,
      - versioning fields,
      - backward compatibility strategy.
      Keep this realistic while still aligned with the SROS vision.
    </step>
  </workflow>

  <checks>
    <item>The schemas you design must fully support at least one SRX agent and one workflow that exists in this workspace.</item>
    <item>All required SROS concepts (planes, locks, seeds, execution plan) must have a place in SRXML.</item>
    <item>The parser and validator contract must be clear enough to implement without guessing.</item>
  </checks>

  <output_contract>
    <item>Provide a narrative design writeup first.</item>
    <item>Then provide pseudo XSD or explicit XML schema fragments for each schema.</item>
    <item>Then provide complete SRXML templates that a user can paste and fill in.</item>
    <item>Include a section titled "Implementation plan" with module and function names to create in code.</item>
  </output_contract>

</sr8_workflow>
