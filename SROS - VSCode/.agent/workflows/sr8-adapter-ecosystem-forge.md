---
description: SR8 - Adapter Ecosystem Forge
---

<sr8_workflow
  id="SR8.SROS.AdapterEcosystemForge.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Adapter Ecosystem Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Adapter Ecosystem Forge</system_name>
    <purpose>
      Define and implement the unified adapter layer for SROS v1:
      Models, Tools, and Storage as strict adapters behind shared interfaces,
      fully enforcing Law 1 that models are adapters and SROS is the OS.
    </purpose>
  </identity>

  <context>
    <item>Adapters live under <code>sros/adapters/</code> and plug into Kernel and Runtime.</item>
    <item>They must be swappable, testable, and governed, not hard wired into business logic.</item>
    <item>They must expose telemetry for Governance and MirrorOS, including cost and latency.</item>
  </context>

  <inputs>
    <item>Existing adapter modules, if any, in <code>sros/adapters/models|tools|storage</code>.</item>
    <item>Blueprint requirements for OpenAI, Gemini, local LLM, HTTP tools, and storage targets.</item>
    <item>Runtime expectations for model invocation, tool calling, and storage operations.</item>
  </inputs>

  <objectives>
    <item>Define base interfaces for ModelAdapter, ToolAdapter, and StorageAdapter.</item>
    <item>Define a registration and discovery mechanism for adapters.</item>
    <item>Design configuration schemas for selecting adapters per tenant and environment.</item>
    <item>Specify telemetry and governance hooks for all adapter calls.</item>
    <item>Provide reference implementations for Gemini, OpenAI, local LLM, HTTP tools, and local storage.</item>
  </objectives>

  <workflow>
    <step order="1" id="adapter_principles">
      Clarify adapter principles:
      - SROS core never imports vendor SDKs directly outside adapter modules.
      - All model invocations go through ModelAdapter interface.
      - All external actions go through ToolAdapter or StorageAdapter.
      - Adapters must degrade gracefully when not configured.
    </step>

    <step order="2" id="base_interfaces">
      Design base interfaces in <code>adapters/base.py</code> or similar:
      - ModelAdapter:
        * <code>generate(prompt, tools, context)</code>,
        * optional streaming and images support,
        * returns standardized Result with text, tokens, cost, metadata.
      - ToolAdapter:
        * <code>invoke(tool_name, args)</code>,
        * handles HTTP, shell, browser, or custom tools.
      - StorageAdapter:
        * <code>get</code>, <code>put</code>, <code>list</code>, <code>delete</code>.
      Include typed error classes and timeouts.
    </step>

    <step order="3" id="adapter_registry">
      Design adapter registry module:
      - Registration API keyed by adapter type and name.
      - Lookup API that respects tenant and environment configuration.
      - Fallback logic when preferred adapter is unavailable.
      - Integration with Kernel and Runtime contexts for injection.
    </step>

    <step order="4" id="model_adapters_design">
      Design concrete model adapters:
      - <code>OpenAIModelAdapter</code>,
      - <code>GeminiModelAdapter</code>,
      - <code>LocalLLMAdapter</code>.
      Each must:
      - map SROS prompts to provider payloads,
      - expose tools where supported,
      - surface token usage and cost estimates,
      - emit <code>adapter.model.call</code> events via EventBus and MirrorOS.
    </step>

    <step order="5" id="tool_adapters_design">
      Design tool adapters:
      - <code>HTTPToolAdapter</code> for REST calls with safety filters,
      - <code>BrowserToolAdapter</code> for browsing tasks where allowed,
      - <code>GitHubToolAdapter</code> for repo interactions.
      Define how they:
      - validate inputs,
      - enforce governance policies,
      - log activity to audit_log and witness.
    </step>

    <step order="6" id="storage_adapters_design">
      Design storage adapters:
      - FileSystemAdapter,
      - S3Adapter,
      - GCSAdapter,
      - LocalSQLiteAdapter for structured data.
      Each must support configuration via <code>sros_config.yml</code> and expose health checks and capacity warnings.
    </step>

    <step order="7" id="config_schema">
      Define configuration schema for adapters:
      - per tenant adapter selection,
      - per environment overrides,
      - secrets referenced by key names, not hard coded.
      Provide example config snippets for common setups.
    </step>

    <step order="8" id="governance_mirroros_hooks">
      Specify how adapters integrate with Governance and MirrorOS:
      - pre call governance check (policy_engine) for high risk tools and models,
      - post call recording of metrics and traces,
      - risk flags when policies are bypassed or near limits.
    </step>

    <step order="9" id="tests_and_examples">
      Define tests:
      - unit tests for adapters with mocked provider SDKs,
      - adapter registry tests for lookup and fallback,
      - integration tests with Runtime agents using fake adapters,
      - example scripts showing adapter swapping without code changes in agents.
    </step>
  </workflow>

  <checks>
    <item>No SROS core module should depend directly on vendor SDKs.</item>
    <item>Adapters must be selectable per tenant from config without code edits.</item>
    <item>All adapter calls must produce telemetry for MirrorOS and Governance.</item>
  </checks>

  <output_contract>
    <item>Adapter interface definitions and registry design.</item>
    <item>Concrete list of adapter implementations to build now vs later.</item>
    <item>Config schema and example configurations.</item>
    <item>Test and example plan proving Law 1 enforcement.</item>
  </output_contract>

</sr8_workflow>
