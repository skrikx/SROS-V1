# SROS v1 Pilot Evaluation Guide

> For CTOs, VPs of Engineering, compliance leads, and platform engineers
> evaluating governed AI agent execution.

---

## Who This Pilot Is For

This evaluation is designed for organizations that are:

- **Deploying AI agents** into workflows that touch regulated data,
  customer-facing systems, or internal infrastructure.
- **Blocked by compliance** because there is no audit trail, policy
  enforcement, or reproducibility for agent execution.
- **Building multi-agent systems** and need governance between agents
  rather than relying on prompt-level restrictions.
- **Evaluating observability** for AI systems beyond traditional
  application monitoring.

If your agents make decisions, access data, or produce outputs that
matter to your business, this pilot is for you.

---

## What SROS Does in Your Environment

SROS is a **governance and observability runtime** that sits between
your AI agents and the systems they interact with.

### What it does

| Capability | How it works |
|------------|-------------|
| **Policy enforcement** | Every agent action passes through the Governance plane before execution. Policies can allow, deny, or conditionally allow actions based on risk level, data sensitivity, and scope. |
| **Execution receipts** | Every workflow produces a JSON receipt capturing each step, each policy verdict, each drift measurement, and a hash-chained audit trail. |
| **Drift monitoring** | The MirrorOS plane continuously monitors agent behavior against expected baselines and flags deviations before they become incidents. |
| **Model-agnostic execution** | Agents are wired through adapters. Swap Gemini for OpenAI or a local model without changing governance logic. |
| **Declarative workflows** | Define agent workflows in SRXML (Sovereign XML). The runtime enforces step ordering, agent assignment, and policy checks per step. |

### What it does not do

- SROS does **not** replace your LLM. It governs what agents built on
  LLMs are allowed to do.
- SROS does **not** replace your existing observability stack. It adds
  a governance-specific observability layer.
- SROS does **not** require you to rewrite your agents. It wraps
  execution in a governed runtime.
- SROS does **not** handle model training, fine-tuning, or inference
  optimization.

---

## A Realistic 2-Week Pilot Plan

### Week 1: Understand and Integrate

| Day | Activity | Output |
|-----|----------|--------|
| 1 | Clone repo, install, run `sros run-demo` or `sros demo-fintech` | Inspect governance receipt |
| 2 | Review industry examples matching your domain | Identify governance patterns |
| 3 | Write a custom SRXML workflow for one internal use case | Custom workflow file |
| 4 | Configure governance policies for your data sensitivity requirements | Policy definitions |
| 5 | Run your custom workflow and inspect the receipt | First governed execution |

### Week 2: Evaluate and Decide

| Day | Activity | Output |
|-----|----------|--------|
| 6-7 | Integrate with your existing LLM adapter (Gemini, OpenAI, or local) | Live model execution |
| 8 | Run a multi-step workflow with real governance constraints | End-to-end governed run |
| 9 | Review receipts with your compliance team | Compliance feedback |
| 10 | Compile findings and make a go/no-go recommendation | Evaluation report |

---

## Inputs Needed from the Pilot Customer

| Input | Why |
|-------|-----|
| One representative agent workflow (2-5 steps) | Grounds the pilot in a real use case |
| Data sensitivity classification for your domain | Configures governance policies |
| Preferred LLM provider (Gemini, OpenAI, local) | Configures the adapter |
| Compliance requirements (HIPAA, SOC2, ECOA, etc.) | Defines policy evaluation criteria |
| Designated engineer (1 person, part-time) | Runs the pilot and reviews outputs |

---

## Outputs and Receipts the Pilot Produces

By the end of the pilot, your organization will have:

1. **A governed workflow definition** in SRXML for one real use case.
2. **Execution receipts** showing every step, every policy verdict,
   and every drift score from real agent runs.
3. **A compliance report** based on governance receipt data.
4. **A clear answer** on whether governed agent execution solves
   your compliance or observability blocker.

### Sample Receipt Structure

```json
{
  "workflow_id": "your_workflow",
  "status": "success",
  "steps": [
    {
      "agent": "your_agent",
      "governance": {
        "verdict": "allow_with_conditions",
        "conditions": ["PII fields blocked", "Output limited to summaries"]
      },
      "mirror": {
        "drift_score": 0.08,
        "drift_detected": false
      }
    }
  ],
  "receipt_chain": { "chain_hash": "a1b2c3d4..." }
}
```

---

## What Engineering Learns

- Whether agent execution can be governed without degrading latency
  or developer experience.
- How policy enforcement integrates with existing CI/CD and testing
  workflows.
- Whether SRXML workflow definitions scale to complex multi-agent
  scenarios.
- What the integration cost is for adding SROS to an existing stack.

## What Compliance and Governance Learns

- Whether execution receipts satisfy audit trail requirements.
- Whether policy enforcement granularity matches your regulatory needs.
- Whether drift detection provides early warning for agent behavior
  issues.
- Whether the receipt format integrates with existing compliance
  reporting.

---

## Success Criteria

The pilot is successful if:

- [ ] A real workflow runs end-to-end under SROS governance.
- [ ] Receipts capture every policy decision with enough detail
      for audit review.
- [ ] The compliance team confirms the receipt format meets their
      documentation requirements.
- [ ] Engineering confirms integration effort is proportional to
      value delivered.

The pilot is not successful if:

- Governance adds unacceptable latency.
- Policy definitions cannot express your real constraints.
- Receipt output does not satisfy your auditors.

---

## How to Start

1. **Self-serve**: Clone the repo and follow the
   [quickstart](../README.md#quickstart-2-minutes). Run the demo.
   Inspect the receipt. Review the [industry examples](../examples/).

2. **Guided evaluation**: Open an issue on the repository or reach
   out to discuss a structured pilot with engineering support.

3. **Enterprise inquiry**: For organizations requiring a formal
   evaluation with SLA and dedicated support, contact the maintainers
   through the repository.

---

> **Alpha Notice**: SROS v1 is in Alpha. This pilot guide describes
> capabilities that are functional in simulation mode. Full
> LLM-integrated production execution is on the roadmap. The
> governance architecture, receipt format, and policy model are stable
> and representative of the production design.
