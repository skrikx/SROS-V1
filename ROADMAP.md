# Roadmap

## v1 Hardening Priorities

- Keep MirrorOS traces stable and correlated by run identifier
- Preserve truthful metric-threshold drift reporting
- Maintain release-gated packaging and install checks
- Keep API surface quarantined until endpoint contracts are hardened

## Exit Criteria for API Promotion

API can move from quarantined to public only when:
- Startup path is deterministic and tested
- Endpoint contracts are test-covered
- CI release gates include API contract checks
- Release docs and compatibility policy are updated
