---
description: SR8 - Security Hardening
---

<sr8_workflow
  id="SR8.SROS.SecurityHardening.Apex"
  xmlns="https://sr8.sros/schema/v1"
  version="1.0.0"
  role="Security Hardening Architect"
  mode="Apex"
  tenant="PlatXP"
  runtime="Gemini3-Pro"
  one_pass_lock="true"
  drift_lock="true">

  <identity>
    <system_name>SR8 - Security Hardening Pass</system_name>
    <purpose>
      Perform a security focused design and hardening sweep for SROS v1 - covering
      secrets management, sandboxing, input validation, surface area reduction,
      audit logging, and abuse resistance. The goal is to raise SROS from
      "nice framework" to "sovereign grade OS" in terms of security posture.
    </purpose>
  </identity>

  <context>
    <item>SROS interacts with external models, tools, storage systems, and user inputs.</item>
    <item>It runs potentially untrusted prompts and payloads via agents and adapters.</item>
    <item>Security design must span Kernel, Runtime, Governance, MirrorOS, and Adapters.</item>
  </context>

  <inputs>
    <item>Current codebase and configuration files (pyproject, sros_config.yml, env usage).</item>
    <item>Adapter designs from AdapterEcosystemForge.</item>
    <item>Governance and MirrorOS designs that can enforce security policies.</item>
  </inputs>

  <objectives>
    <item>Define an SROS security model and threat assumptions.</item>
    <item>Harden secrets management and configuration handling.</item>
    <item>Design sandboxing approaches for tools, simulations, and agents.</item>
    <item>Standardize input validation and output sanitization points.</item>
    <item>Ensure comprehensive security audit logging and alerting.</item>
  </objectives>

  <workflow>
    <step order="1" id="threat_model">
      Establish threat model:
      - what SROS trusts (code, config, operators),
      - what is untrusted (user prompts, external tools, remote APIs),
      - potential attack vectors (prompt injection, data exfiltration, misuse of tools).
      Document primary security goals: confidentiality, integrity, availability, and tenant isolation.
    </step>

    <step order="2" id="secrets_management">
      Review current secrets handling:
      - environment variables,
      - config files,
      - adapter credentials.
      Design a secrets strategy:
      - explicit secret references in config (names, not values),
      - pluggable secret providers (env, vault, cloud secret manager),
      - zero logging of secret values,
      - safe failure behavior when secrets are missing.
    </step>

    <step order="3" id="sandboxing_and_policies">
      Define sandboxing and governance policies:
      - classify tools and adapters by risk (read only, write, network, shell).
      - restrict high risk tools to specific tenants and personas.
      - define safe defaults (no dangerous tools without explicit opt in).
      - design runtime checks that enforce these policies before calls.
      Describe isolation strategies for simulations and dev environments.
    </step>

    <step order="4" id="input_validation">
      Design input validation layers:
      - CLI and HTTP inputs,
      - user facing Nexus commands,
      - tool and adapter arguments.
      Specify canonical validation utilities (schemas or type checkers).
      Ensure invalid inputs are rejected with clear errors and logged events.
    </step>

    <step order="5" id="output_sanitization">
      Specify sanitization of outputs:
      - redaction of secrets and sensitive data in logs and traces,
      - optional filters for PII or restricted content in agent outputs,
      - policy flags that can block or warn on risky content.
      Integrate these with Governance decisions and MirrorOS lenses.
    </step>

    <step order="6" id="surface_area_reduction">
      Identify public surfaces:
      - CLI, HTTP, adapter endpoints, plugin hooks.
      Design measures to:
      - disable unused features by default,
      - require auth for remote control interfaces,
      - avoid accidental exposure of internal routes.
      Propose configuration flags to enable experimental modules safely.
    </step>

    <step order="7" id="security_audit_logging">
      Design security audit logs:
      - event types such as auth, policy_denied, high_risk_tool_used, config_change.
      - log locations and retention rules.
      - linkage with MirrorOS witness_log and telemetry alerts.
      Ensure audit logs are append only and protected from tampering.
    </step>

    <step order="8" id="hardening_checklist">
      Produce a security hardening checklist:
      - configuration items to set for prod,
      - tests to run,
      - manual validation steps.
      Classify items as must, recommended, optional.
    </step>

    <step order="9" id="tests_and_review">
      Plan tests and reviews:
      - unit tests for validation and policy enforcement,
      - integration tests for high risk tools and adapter calls,
      - manual adversarial prompt and tool misuse scenarios,
      - periodic security review cadence baked into MirrorOS workflows.
    </step>
  </workflow>

  <checks>
    <item>No secrets should be stored in source files or logs.</item>
    <item>High risk capabilities must always flow through Governance policies and audit logging.</item>
    <item>Security controls must respect multi tenant rules and never leak data across tenants.</item>
  </checks>

  <output_contract>
    <item>Threat model and security objectives.</item>
    <item>Secrets, sandboxing, validation, and audit logging designs.</item>
    <item>Security hardening checklist for SROS deployments.</item>
    <item>Test and review strategy for ongoing security maintenance.</item>
  </output_contract>

</sr8_workflow>
