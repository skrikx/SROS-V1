# SROS v1 Release Checklist

## Pre-Release

### Code Quality
- [x] All tests passing (`python run_all_tests.py`)
- [x] CLI commands verified working
- [x] API endpoints validated
- [ ] Full coverage report generated
- [ ] Static analysis (if applicable)

### Documentation
- [x] README.md complete with badges and quickstart
- [x] ARCHITECTURE.md with diagrams
- [x] CONTRIBUTING.md with guidelines
- [x] CHANGELOG.md with version history
- [x] SROS_STUDY_GUIDE_v1.md expanded
- [x] PLANES.md with module reference
- [x] API_REFERENCE.md accurate
- [x] CLI_GUIDE.md accurate
- [x] DEMO.md accurate

### Repository
- [x] Git repository initialized
- [x] .gitignore configured
- [x] VERSION file created (1.0.0-alpha)
- [x] SRXML schemas organized
- [x] pyproject.toml metadata complete
- [ ] All __init__.py exports verified
- [ ] License file verified

### Infrastructure
- [ ] Docker configuration (optional for alpha)
- [ ] CI/CD pipeline (optional for alpha)
- [ ] PyPI publishing setup (optional for alpha)

---

## Release Steps

### 1. Final Verification

```bash
# Clean install test
pip uninstall sros -y
pip install -e .

# Run all tests
python run_all_tests.py

# Verify CLI
sros --help
sros status system
sros workflow run examples/hello_world_workflow.srxml
```

### 2. Version Bump (if needed)

```bash
# Check current version
cat VERSION

# Update if needed
echo "1.0.0-alpha" > VERSION
```

### 3. Git Tagging

```bash
# Create release tag
git tag -a v1.0.0-alpha -m "SROS v1.0.0-alpha release"

# Push tag (when ready)
git push origin v1.0.0-alpha
```

### 4. Create Release Archive

```bash
# Create distribution
python -m build

# Or create zip archive
git archive --format=zip --output=sros-v1.0.0-alpha.zip HEAD
```

### 5. Release Notes

Include in release:
- Summary of features
- Known limitations (Alpha status)
- Installation instructions
- Breaking changes (if any)
- Contributors

---

## Post-Release

- [ ] Update documentation if needed
- [ ] Monitor for issues
- [ ] Plan for next release

---

## Known Limitations (Alpha)

1. **CLI Entry Point**: May require `python -m sros.nexus.cli.main` instead of `sros` command
2. **External Models**: Require API keys (GEMINI_API_KEY, OPENAI_API_KEY)
3. **Memory Backend**: SQLite only, no production database support yet
4. **Blueprint Gaps**: Some modules from blueprint not yet implemented:
   - Kernel: scheduler, security, heartbeat daemons (partial)
   - MirrorOS: replay, reflection, snapshot
   - Governance: eval engine, risk registry

---

## Release History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0-alpha | 2024-12-17 | Initial alpha release |
