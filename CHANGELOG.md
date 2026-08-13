# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-08-12

### Added

- Added specification-alignment documentation set:
  - `MIGRATION.md`
  - `CONFORMANCE_MATRIX.md`
  - `ERROR_MODEL.md`
  - `LOGGING.md`
  - `SEMANTICS.md`
  - `FAQ.md`

### Changed

- Runtime semantics aligned with FlitFlow Core Spec v1.1:
  - `switch` boolean key normalization (`true` / `false` lowercase)
  - `switch` no-match and no-`default` behavior:
    - normal completion
    - unresolved-branch warning log
  - nested step execution uses shallow-copied child state
  - out-of-loop `BREAK` / `CONTINUE`:
    - warning log
    - ignored as control signal
    - execution continues
- Conformance tests updated for v1.1 behaviors.

### Compatibility Notes

- Some edge-case behavior may differ from earlier 1.0 runtime behavior.
- Review `MIGRATION.md` before upgrading embedded workflows.
