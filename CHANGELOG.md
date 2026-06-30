# Changelog

## v0.1.0-candidate

### Added

- Added `wing-definition.schema.json` as the declarative input schema for generator definitions.
- Added `wing-definition.example.yaml` with Finder, Analyst, Repair, Verifier, Boundary, Human Gate, and Trace Core wings.
- Added `generate_multi_wing_schema.py` for producing a generated Multi-Wing Defensive Orchestration JSON Schema.
- Added `validate_examples.py` for validating the wing definition example and generated schema syntax.
- Added GitHub Actions workflow for CI validation.

### Purpose

v0.1 establishes the Generator Seed Layer.

This version turns declarative wing definitions into a CI-verifiable generated orchestration schema.

### Structural Position

```text
Yin-Yang Mythos Regulator
= defensive regulation protocol

Multi-Wing Orchestration Generator
= generator layer for defensive multi-wing structures
