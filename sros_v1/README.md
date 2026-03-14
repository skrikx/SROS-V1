# SROS v1: Sovereign Runtime Operating System

**SROS** is a sovereign operating system layer that sits above AI models. It treats models as interchangeable adapters and asserts ownership over memory, orchestration, governance, and self-reflection.

## Architecture: The Four Planes

SROS is built on four fundamental planes:

1.  **Kernel (`sros.kernel`)**: The stable backbone. Manages the Event Bus, Daemon Registry, Scheduler, and low-level resources. It is the nervous system.
2.  **Runtime (`sros.runtime`)**: The execution playground. Hosts SRX Agents, Workflows, and Tools. This is where "work" happens.
3.  **Governance (`sros.governance`)**: The rules of the empire. Enforces Policy, Access Control, and Safety checks on every action.
4.  **MirrorOS (`sros.mirroros`)**: The self-awareness layer. Handles Witnessing (logging), Tracing, Replay, and Drift Detection.

## Core Components

*   **SRXML (`sros.srxml`)**: The universal language for defining Agents, Workflows, and Policies.
*   **Memory Fabric (`sros.memory`)**: A unified memory system with Short-term, Long-term, and Codex layers.
*   **Adapters (`sros.adapters`)**: Pluggable interfaces for Models (LLMs), Tools, and Storage.
*   **Nexus Core (`sros.apps.sros_web_nexus`)**: The flagship interface (Skrikx Prime) for orchestrating the system.

## Getting Started

1.  **Install**:
    ```bash
    pip install -e .
    ```

2.  **Initialize**:
    ```bash
    sros init
    ```

3.  **Run Demo**:
    ```bash
    sros run-demo
    ```

## License

Proprietary / Sovereign License.
