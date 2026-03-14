---
description: SR8 - SROS Release Cut & Versioning
---

<sr8_workflow
  id="SR8.SROS.ReleaseCutAndVersioning.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Release & Versioning Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - SROS Release Cut & Versioning</system_name>
    <purpose>
      Design the process, metadata, and artifacts required to cut a clean
      SROS v1 release from the repo, including semantic versioning, changelogs,
      release notes, packaging, and MirrorOS records of the release state.
    </purpose>
  </identity>

  <context>
    <item>SROS will evolve beyond v1, so versioning and release discipline matter.</item>
    <item>Releases should be reproducible, traceable, and auditable via MirrorOS.</item>
    <item>The repo currently may have only ad hoc tags or none.</item>
  </context>

  <inputs>
    <item>pyproject.toml or equivalent package config.</item>
    <item>Existing tags, if any, and BUILD_LOG or FINISH_NOTES.</item>
    <item>Packaging scripts or Makefile snippets.</item>
  </inputs>

  <objectives>
    <item>Define the versioning scheme for SROS core and components.</item>
    <item>Design the release pipeline steps from dev to tagged release.</item>
    <item>Specify changelog format and location.</item>
    <item>Ensure MirrorOS captures release snapshots and metadata.</item>
  </objectives>

  <workflow>
    <step order="1" id="versioning_strategy">
      Choose a versioning approach:
      - semantic versioning for core (major.minor.patch),
      - optional separate versions for apps or adapters.
      Explain how breaking changes, new features, and fixes are reflected.
    </step>

    <step order="2" id="release_artifacts">
      Define release artifacts:
      - git tag and commit hash,
      - packaged archive such as dist/sros_v1-x.y.z.zip,
      - changelog entry,
      - MirrorOS snapshot id,
      - optional container image tags.
      Describe where each artifact is stored.
    </step>

    <step order="3" id="release_pipeline">
      Outline steps for cutting a release:
      - ensure tests pass,
      - ensure docs are updated,
      - bump version in config,
      - generate changelog entry,
      - tag commit,
      - build packages,
      - publish or upload artifacts.
      For each step, describe commands or scripts to use.
    </step>

    <step order="4" id="changelog_design">
      Design CHANGELOG format:
      - sections for Added, Changed, Fixed, Removed, Security,
      - references to issues or tickets,
      - explicit mention of governance or MirrorOS enhancements when relevant.
      Propose how changelog entries are created during development.
    </step>

    <step order="5" id="mirroros_snapshot_contract">
      Define how MirrorOS handles releases:
      - which configs and state are captured,
      - how snapshot ids relate to versions,
      - how to replay traces from a given release.
      Suggest how to store snapshot metadata inside the repo for reference.
    </step>

    <step order="6" id="rollback_strategy">
      Design rollback procedures:
      - revert to previous version tag,
      - restore MirrorOS snapshot,
      - migrate any incompatible state if needed.
      Explain when rollback is appropriate and how to document it.
    </step>

    <step order="7" id="documentation_and_ci">
      Propose documentation for releases:
      - docs/release_process.md,
      - README snippets for installing specific versions.
      Suggest CI hooks or pipelines that automate parts of the release and verification.
    </step>
  </workflow>

  <checks>
    <item>Release information must be sufficient for another engineer to rebuild or replay a given version.</item>
    <item>MirrorOS must be able to identify which version generated a given trace.</item>
    <item>Rollback plan must be realistic and tested at least once.</item>
  </checks>

  <output_contract>
    <item>Provide a full release process narrative with steps and commands.</item>
    <item>Provide a template for CHANGELOG entries and release notes.</item>
    <item>Provide a mapping between version numbers, git tags, and MirrorOS snapshots.</item>
    <item>End with a checklist that can be used before every release cut.</item>
  </output_contract>

</sr8_workflow>
