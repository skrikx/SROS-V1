---
description: SR8 - Multi-Tenant Isolation
---

<sr8_workflow
  id="SR8.SROS.MultiTenantIsolation.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Multi Tenant Isolation Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Multi Tenant Isolation</system_name>
    <purpose>
      Design and specify true multi tenant isolation for SROS v1 - covering
      configuration, Kernel and Memory boundaries, adapter selection, telemetry,
      governance, and MirrorOS traces so that tenants share infrastructure but
      never data or control paths.
    </purpose>
  </identity>

  <context>
    <item>SROS is intended to run multiple tenants on one installation.</item>
    <item>Tenants may have different adapters, codex packs, and policies.</item>
    <item>Isolation must be enforced at all layers, not just at config level.</item>
  </context>

  <inputs>
    <item>Current use of <code>tenant</code> fields in SRXML, config, and code.</item>
    <item>Memory and Codex fabric design from MemoryCodexFabric workflow.</item>
    <item>Adapter and Governance designs that must become tenant aware.</item>
  </inputs>

  <objectives>
    <item>Define the tenant model and identity representation.</item>
    <item>Design per tenant configuration loading and validation.</item>
    <item>Ensure all Memory, Codex, Telemetry, and Traces are tenant scoped.</item>
    <item>Define adapter selection and policy enforcement per tenant.</item>
    <item>Specify tests that prove tenants cannot see or affect each other.</item>
  </objectives>

  <workflow>
    <step order="1" id="tenant_model">
      Define tenant model:
      - tenant_id, display_name, environment, allowed_features, default_adapters.
      - relation to users and roles if present.
      - location of tenant definitions (config files, database, or SRXML).
      Clarify how tenant_id is propagated through events, memory keys, traces.
    </step>

    <step order="2" id="config_scoping">
      Design config scoping:
      - base config for installation,
      - per tenant overlays with adapters, policies, codex packs,
      - resolution order (global, environment, tenant).
      Provide examples of <code>sros_config.yml</code> with multiple tenants.
    </step>

    <step order="3" id="kernel_runtime_isolation">
      Specify Kernel and Runtime isolation:
      - KernelContext carries tenant aware handles for Memory, Adapters, Governance.
      - event topics include tenant_id where appropriate.
      - daemon responsibilities for per tenant health and limits.
      Consider whether any daemons should be per tenant processes or logically partitioned.
    </step>

    <step order="4" id="memory_and_codex_isolation">
      Design Memory and Codex isolation:
      - per tenant namespaces in keys and indexes.
      - default layers and codex packs per tenant.
      - configuration that prevents cross tenant reads without superuser role.
      Outline tests that attempt cross tenant access and must fail.
    </step>

    <step order="5" id="adapter_and_policy_scoping">
      Specify adapter and governance scoping:
      - adapter choices per tenant (model provider, tools, storage).
      - policy sets per tenant for actions and sensitive tools.
      - fail safe behavior if a tenant refers to unavailable adapter or policy.
      Ensure this is enforced centrally in adapter registry and policy_engine.
    </step>

    <step order="6" id="telemetry_and_traces">
      Define telemetry and MirrorOS trace isolation:
      - telemetry events tagged with tenant_id.
      - queries always filter by tenant_id unless superuser context is used.
      - lenses and dashboards default to current tenant view.
      Provide guidelines for secure multi tenant dashboard implementations.
    </step>

    <step order="7" id="limits_and_quotas">
      Design tenant level limits:
      - rate limits for adapter calls and simulations,
      - memory and storage quotas,
      - concurrency caps for workflows.
      Describe how governance and telemetry collaborate to enforce and report limits.
    </step>

    <step order="8" id="tests_and_red_team">
      Plan tests:
      - automated tests that instantiate two or more tenants and verify isolation,
      - scenarios trying to access another tenant's memory, codex, telemetry, or traces,
      - red team style manual tests for misconfiguration, especially default tenants.
    </step>
  </workflow>

  <checks>
    <item>Every SROS API that touches data or state must accept or infer a tenant_id.</item>
    <item>It must be impossible for one tenant to access another's data using standard APIs.</item>
    <item>Telemetry and dashboards must never mix tenants silently.</item>
  </checks>

  <output_contract>
    <item>Tenant model, config scoping, and identity propagation design.</item>
    <item>Isolation rules for Kernel, Runtime, Memory, Adapters, and MirrorOS.</item>
    <item>Limit and quota model per tenant.</item>
    <item>Test plan and red team scenarios that prove isolation.</item>
  </output_contract>

</sr8_workflow>
