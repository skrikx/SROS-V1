---
description: SR8 - Knowledge Pack Builder
---

<sr8_workflow
  id="SR8.SROS.KnowledgePackBuilder.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Codex Pack Builder"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Knowledge Pack Builder</system_name>
    <purpose>
      Define the workflow and tooling for creating, indexing, validating,
      and publishing Codex Packs in SROS v1, turning raw text and docs into
      structured, queryable knowledge for agents and workflows.
    </purpose>
  </identity>

  <context>
    <item>Codex packs live under <code>sros/codex/packs/</code> and are accessed via CodexIndex and CodexSearch.</item>
    <item>They power research, playbooks, governance rules, and system knowledge.</item>
    <item>The builder must be repeatable and safe, with validation steps.</item>
  </context>

  <inputs>
    <item>Raw source material: markdown, PDFs, docs, configs.</item>
    <item>Codex module stubs: <code>codex_index.py</code>, <code>codex_loader.py</code>, <code>codex_search.py</code>.</item>
    <item>Memory and vector backend configuration for indexing.</item>
  </inputs>

  <objectives>
    <item>Define Codex Pack structure on disk and in metadata.</item>
    <item>Design ingestion and chunking pipeline for raw content.</item>
    <item>Design indexing pipeline using vector or keyword search backends.</item>
    <item>Define validation and quality checks for packs.</item>
    <item>Expose a workflow and CLI to build and publish packs.</item>
  </objectives>

  <workflow>
    <step order="1" id="pack_structure">
      Specify pack structure:
      - root folder per pack: <code>sros/codex/packs/{pack_id}/</code>,
      - subfolders: <code>raw/</code>, <code>processed/</code>, <code>index/</code>, <code>meta/</code>,
      - metadata file <code>meta.json</code> with id, title, description, source, licenses, version, tags.
      Ensure versioning fields are included for future updates.
    </step>

    <step order="2" id="ingestion_pipeline">
      Design ingestion pipeline:
      - collect raw files from configured locations,
      - normalize to text with metadata (source, section, page),
      - chunk text using size and semantic cues,
      - write processed chunks to <code>processed/</code> with stable ids.
      Describe how this is implemented in a builder module.
    </step>

    <step order="3" id="indexing_pipeline">
      Design indexing pipeline:
      - select backend (vector, keyword, hybrid) via config,
      - build indices and store under <code>index/</code>,
      - store mapping from chunk ids to index entries,
      - compute summary statistics such as token count and coverage.
      Define how CodexIndex and CodexSearch will use these artifacts.
    </step>

    <step order="4" id="validation_checks">
      Define validation checks:
      - metadata completeness and schema validation,
      - minimum content size and diversity,
      - sample search queries to ensure results are meaningful,
      - duplication detection and noise filtering.
      Describe how validation results are reported to the user.
    </step>

    <step order="5" id="governance_and_licenses">
      Address governance:
      - record data sources and licenses in metadata,
      - flag packs that contain sensitive or restricted content,
      - provide hooks for Governance policies to allow or deny usage.
      Ensure packs can be disabled per tenant via config.
    </step>

    <step order="6" id="builder_workflow">
      Design the builder workflow as code and CLI:
      - <code>sros build-codex-pack --id</code>,
      - prompts for source paths and config when needed,
      - runs ingestion, indexing, and validation steps,
      - prints summary and warnings.
      Define how Agent personas (e.g. Researcher) can trigger this as well.
    </step>

    <step order="7" id="tests_and_examples">
      Plan tests and examples:
      - unit tests for ingestion and chunking logic,
      - tests for metadata validation and schema enforcement,
      - integration test that builds a small demo pack and runs queries,
      - example config for core SROS codex, research codex, and playbooks codex.
    </step>
  </workflow>

  <checks>
    <item>Every Codex Pack must have complete metadata and pass validation before use.</item>
    <item>Packs must be tenant aware and disableable via config and Governance.</item>
    <item>Builders must work in an offline dev mode with only local files.</item>
  </checks>

  <output_contract>
    <item>Codex Pack on disk structure and metadata schema.</item>
    <item>Ingestion and indexing pipeline design with function signatures.</item>
    <item>Validation and governance model for Codex Packs.</item>
    <item>Builder workflow description plus CLI and test plan.</item>
  </output_contract>

</sr8_workflow>
