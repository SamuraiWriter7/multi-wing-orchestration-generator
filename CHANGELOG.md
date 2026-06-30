# Changelog

## v0.2.0-candidate

### Added

* Added automatic `handoff_rules` generation from each wing's `handoff_to` declarations.
* Added generated orchestration example output.
* Added validation for generated examples against generated schemas.
* Added duplicate `wing_id` detection.
* Added invalid handoff reference detection.
* Added internal validation for generated handoff rules.

### Changed

* Updated `wing-definition.schema.json` from `0.1.0` to `0.2.0`.
* Added `target.output_example_filename` to support generated example output.
* Updated `generate_multi_wing_schema.py` to produce both schema and example artifacts when enabled.
* Updated `validate_examples.py` to validate wing graph consistency.
* Strengthened CI validation from schema syntax checking to generated artifact consistency checking.

### Purpose

v0.2 establishes the Handoff Rule Expansion layer.

This version turns static wing declarations into a generated orchestration graph.

```text
v0.1 Generator Seed Layer
= define and generate schema

v0.2 Handoff Rule Expansion
= generate and validate wing transitions
```

### Structural Position

The generator now checks whether declared wing transitions are structurally valid.

This prevents broken or drifting orchestration graphs from passing silently.

### Generated Artifacts

v0.2 generates:

```text
generated/generated-multi-wing-defensive-orchestration.schema.json
generated/generated-multi-wing-defensive-orchestration.example.yaml
```

### Validation Scope

v0.2 validates:

* the source wing definition example
* duplicate `wing_id` values
* invalid `handoff_to` references
* generated JSON Schema syntax
* generated example YAML against the generated schema
* generated handoff rule references

### Next Direction

The next likely version is:

```text
v0.3 — Blocking Condition Expansion
```

Planned direction:

* classify blocking conditions by severity
* generate boundary escalation maps
* connect blocking conditions to human review gates
* detect orphan blocking rules
* strengthen safety boundary generation

---

## v0.1.0-candidate

### Added

* Added `schemas/wing-definition.schema.json` as the declarative input schema for generator definitions.
* Added `examples/wing-definition.example.yaml` with Finder, Analyst, Repair, Verifier, Boundary, Human Gate, and Trace Core wings.
* Added `scripts/generate_multi_wing_schema.py` for producing a generated Multi-Wing Defensive Orchestration JSON Schema.
* Added `scripts/validate_examples.py` for validating the wing definition example and generated schema syntax.
* Added GitHub Actions workflow for CI validation.
* Added `README.md` documenting purpose, generator flow, core concepts, usage, and relationship to `Yin-Yang Mythos Regulator`.
* Added `CHANGELOG.md` to record the generator arc.

### Purpose

v0.1 establishes the Generator Seed Layer.

This version turns declarative wing definitions into a CI-verifiable generated orchestration schema.

### Structural Position

```text
Yin-Yang Mythos Regulator
= defensive regulation protocol

Multi-Wing Orchestration Generator
= generator layer for defensive multi-wing structures
```

### Summary

v0.1 created the minimum generator path:

```text
wing definition
↓
generated schema
↓
schema syntax validation
↓
GitHub Actions
```

It established the seed of a defensive orchestration forge.

