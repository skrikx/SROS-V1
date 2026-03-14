# Contributing to SROS

Thank you for your interest in contributing to SROS (Sovereign Runtime Operating System). This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [SRXML Authoring](#srxml-authoring)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Plane-Specific Guidelines](#plane-specific-guidelines)

---

## Code of Conduct

SROS is built on principles of sovereignty, safety, and transparency. Contributors are expected to:

- **Respect the architecture**: Changes should align with the four-plane model
- **Prioritize safety**: All changes must pass governance checks
- **Document thoroughly**: Code without documentation is incomplete
- **Test rigorously**: Untested code is not production-ready

---

## Getting Started

1. **Fork the repository** (if applicable)
2. **Clone locally**:
   ```bash
   git clone <repository-url>
   cd sros-v1-alpha
   ```
3. **Install in development mode**:
   ```bash
   pip install -e .
   ```
4. **Initialize SROS**:
   ```bash
   sros init
   ```
5. **Run tests**:
   ```bash
   python run_all_tests.py
   ```

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (latest version)
- Git

### Recommended IDE Setup

- **VS Code** with Python extension
- Enable format on save with Black
- Configure import sorting with isort

### Environment Variables

Create a `.env` file for local development:

```bash
# Optional: For external model testing
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Debug mode
SROS_DEBUG=true
SROS_LOG_LEVEL=DEBUG
```

---

## Code Style

### Python

SROS follows **PEP 8** with the following additions:

- **Line length**: 100 characters maximum
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style

#### Example

```python
"""Module docstring describing purpose."""

from typing import Optional, List

from pydantic import BaseModel

from sros.kernel.event_bus import EventBus


class MyComponent:
    """Component description.
    
    Attributes:
        name: The component name.
        enabled: Whether the component is active.
    """
    
    def __init__(self, name: str, enabled: bool = True) -> None:
        """Initialize the component.
        
        Args:
            name: The component name.
            enabled: Whether to enable the component.
        """
        self.name = name
        self.enabled = enabled
    
    def process(self, data: dict) -> Optional[dict]:
        """Process incoming data.
        
        Args:
            data: The data to process.
            
        Returns:
            Processed data or None if processing failed.
            
        Raises:
            ValueError: If data is invalid.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        return {"processed": True, **data}
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `kernel_state.py` |
| Classes | PascalCase | `KernelState` |
| Functions | snake_case | `get_state()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _leading_underscore | `_internal_method()` |

---

## SRXML Authoring

SRXML is the primary language for schemas, agents, and workflows.

### Workflow Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<workflow name="example_workflow" version="1.0">
    <metadata>
        <author>Your Name</author>
        <description>Workflow description</description>
    </metadata>
    
    <steps>
        <step id="step_1" agent="architect">
            <task>Analyze the system</task>
        </step>
        
        <step id="step_2" agent="builder" depends_on="step_1">
            <task>Implement the solution</task>
        </step>
    </steps>
</workflow>
```

### Agent Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<agent name="custom_agent" version="1.0">
    <identity>
        <role>Custom Role</role>
        <objective>What this agent does</objective>
    </identity>
    
    <capabilities>
        <capability>code_generation</capability>
        <capability>analysis</capability>
    </capabilities>
    
    <constraints>
        <constraint>Must validate all outputs</constraint>
    </constraints>
</agent>
```

### Validation

Always validate SRXML before committing:

```bash
sros workflow validate path/to/workflow.srxml
```

---

## Testing

### Test Structure

```
tests/
├── fixtures/           # Test data and fixtures
├── integration/        # Integration tests
├── test_*.py          # Unit tests
└── sros_test_suite.py # Master test runner
```

### Writing Tests

```python
"""Tests for the kernel bootstrap module."""

import pytest

from sros.kernel.kernel_bootstrap import KernelBootstrap


class TestKernelBootstrap:
    """Test cases for KernelBootstrap."""
    
    def test_boot_initializes_state(self):
        """Kernel boot should initialize kernel state."""
        bootstrap = KernelBootstrap()
        result = bootstrap.boot()
        
        assert result.success is True
        assert result.state is not None
    
    def test_boot_fails_without_config(self):
        """Kernel boot should fail gracefully without config."""
        bootstrap = KernelBootstrap(config=None)
        
        with pytest.raises(ValueError):
            bootstrap.boot()
```

### Running Tests

```bash
# Run all tests
python run_all_tests.py

# Run specific test file
pytest tests/test_kernel_boot.py

# Run with coverage
pytest --cov=sros tests/

# Run integration tests only
pytest tests/integration/
```

### Test Requirements

- All new code must have corresponding tests
- Minimum 80% coverage for new modules
- Integration tests for cross-plane interactions

---

## Pull Request Process

### Before Submitting

1. **Run all tests**: `python run_all_tests.py`
2. **Check code style**: Ensure PEP 8 compliance
3. **Update documentation**: Add/update relevant docs
4. **Update CHANGELOG**: Add entry for your changes

### PR Description Template

```markdown
## Summary
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Planes Affected
- [ ] Kernel
- [ ] Runtime
- [ ] Governance
- [ ] MirrorOS
- [ ] Support layers

## Testing
Describe tests added or modified.

## Documentation
List documentation updates.
```

### Review Process

1. All PRs require at least one review
2. CI must pass (tests, linting)
3. Documentation must be complete
4. CHANGELOG must be updated

---

## Plane-Specific Guidelines

### Kernel (`sros/kernel/`)

- Changes here affect the entire system
- All changes must be backward compatible
- Event bus modifications require RFC

### Runtime (`sros/runtime/`)

- New agents should extend `AgentBase`
- Workflows must be SRXML-validated
- Session management is critical for state

### Governance (`sros/governance/`)

- Policy changes require security review
- All actions must be auditable
- Cost tracking must be accurate

### MirrorOS (`sros/mirroros/`)

- Witness calls must be non-blocking
- Drift detection thresholds are configurable
- Traces must be retrievable

---

## Getting Help

- **Documentation**: See `docs/` directory
- **Study Guide**: `docs/SROS_STUDY_GUIDE_v1.md`
- **Architecture**: `docs/ARCHITECTURE.md`

---

## License

By contributing to SROS, you agree that your contributions will be licensed under the project's MIT License.
