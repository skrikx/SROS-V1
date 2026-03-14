# SROS v1: Sovereign Runtime Operating System

[![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue.svg)](VERSION)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)]()

> **SROS** is an AI operating system designed to orchestrate complex agentic workflows with strict governance, comprehensive observability, and self-evolution capabilities.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SROS v1 Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   MirrorOS  │  │  Governance │  │   Runtime   │  │  Kernel │ │
│  │  (Plane 4)  │  │  (Plane 3)  │  │  (Plane 2)  │  │(Plane 1)│ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────┤ │
│  │ • Witness   │  │ • Policy    │  │ • Agents    │  │ • State │ │
│  │ • Drift     │  │ • Access    │  │ • Workflows │  │ • Events│ │
│  │ • Telemetry │  │ • Costs     │  │ • Sessions  │  │ • Config│ │
│  │ • Lenses    │  │ • Audit     │  │ • Tools     │  │ • Daemon│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  SRXML │ Memory │ Adapters │ Evolution │ Nexus (CLI/API)        │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Four-Plane Architecture** | Kernel, Runtime, Governance, and MirrorOS planes for clean separation |
| **SRXML Workflows** | Declarative XML-based workflow definitions |
| **Multi-Agent System** | Architect, Builder, Tester, and custom agents |
| **Policy Enforcement** | Governance plane ensures safety and compliance |
| **Self-Evolution** | Ouroboros engine for self-improvement |
| **Multi-Layer Memory** | Short-term, long-term, codex, and vector storage |
| **Model Agnostic** | Pluggable adapters for Gemini, OpenAI, and local models |
| **Full Observability** | MirrorOS witnesses and traces all operations |

---

## 🚀 Quickstart

### Installation

```bash
# Clone and install
git clone <repository_url>
cd SROS-V1
pip install -e .
```

### Initialize

```bash
sros init
```

### Run Demo

```bash
sros run-demo
```



---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and data flows |
| [Study Guide](docs/SROS_STUDY_GUIDE_v1.md) | Learning guide for developers |
| [API Reference](docs/API_REFERENCE.md) | HTTP API documentation |
| [CLI Guide](docs/CLI_GUIDE.md) | Command-line interface |
| [Demo Guide](docs/DEMO.md) | Step-by-step demo walkthrough |
| [Contributing](CONTRIBUTING.md) | Development guidelines |
| [Changelog](CHANGELOG.md) | Version history |

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Unit tests
pytest tests/test_kernel_boot.py
pytest tests/test_srxml_parser.py

# Integration tests
pytest tests/integration/
```

---

## 🔧 CLI Commands

```bash
# Core Config
sros init                    # Initialize SROS config

# Demo
sros run-demo                # Run the SROS sample workflow
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Model API keys (optional)
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Debug mode
SROS_DEBUG=true
SROS_LOG_LEVEL=DEBUG
```

### Configuration File

Edit `sros_config.yml` for system-wide settings.

---

## 📁 Project Structure

```
.
├── sros/                    # Main package
│   ├── kernel/              # Plane 1: Core system
│   ├── runtime/             # Plane 2: Agent execution
│   ├── governance/          # Plane 3: Policy enforcement
│   ├── mirroros/            # Plane 4: Observability
│   ├── srxml/               # SRXML parser and schemas
│   ├── memory/              # Memory backends
│   ├── adapters/            # Model/tool adapters
│   ├── evolution/           # Self-improvement
│   └── nexus/               # CLI and API
├── tests/                   # Test suite
├── examples/                # Example workflows
├── docs/                    # Documentation
├── pyproject.toml           # Package configuration
└── sros_config.yml          # System configuration
```

---

## ⚠️ Alpha Status

> **Note**: SROS v1 is currently in **Alpha**. APIs are subject to change. Review governance policies before production use.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
