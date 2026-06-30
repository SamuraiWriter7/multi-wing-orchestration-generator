# Changelog

## v0.3.0-candidate

### Added

* Added structured blocking condition definitions.
* Added `condition_id`, `description`, `severity`, `escalation_target`, `requires_human_review`, and `trace_required` fields.
* Added automatic `boundary_escalation_map` generation.
* Added duplicate `condition_id` detection.
* Added invalid `escalation_target` detection.
* Added blocking condition policy validation.
* Added generated boundary escalation map validation.

### Changed

* Updated `wing-definition.schema.json` from `0.2.0` to `0.3.0`.
* Changed `blocking_conditions` from string arrays to structured object arrays.
* Updated generated orchestration examples to include structured blocking conditions.
* Updated generated schemas to include `boundary_escalation_map`.
* Strengthened CI validation around defensive routing rules.

### Purpose

v0.3 establishes the Blocking Condition Expansion layer.

This version turns blocking conditions into explicit defensive routing rules.

```text
v0.1 Generator Seed Layer
= define and generate schema

v0.2 Handoff Rule Expansion
= generate and validate wing transitions

v0.3 Blocking Condition Expansion
= generate and validate defensive blocking routes
```

### Structural Position

The generator now checks whether defensive blocking conditions are structurally valid.

A blocking condition is no longer just a warning string.

It is now a routed defensive event with:

* a unique condition identity
* a severity level
* an escalation target
* a human review requirement
* a trace requirement

This prevents unsafe or incomplete defensive routes from passing silently.

### Generated Artifacts

v0.3 generates:

```text
generated/generated-multi-wing-defensive-orchestration.schema.json
generated/generated-multi-wing-defensive-orchestration.example.yaml
```

The generated example now includes:

```text
blocking_conditions
boundary_escalation_map
```

### Validation Scope

v0.3 validates:

* source wing definition example
* duplicate `wing_id` values
* invalid `handoff_to` references
* duplicate `condition_id` values
* invalid blocking condition escalation targets
* critical conditions without human review
* high or critical conditions without trace evidence
* generated JSON Schema syntax
* generated example YAML against the generated schema
* generated handoff rule references
* generated boundary escalation map references

### Expected Validation Output

A successful validation run should look similar to this:

```text
[validate] Wing Definition
[ok] wing-definition.example.yaml is valid
[ok] wing_id values are unique
[ok] handoff references are valid
[ok] condition_id values are unique
[ok] blocking condition escalation targets are valid
[ok] blocking condition policy is valid
[generate] Multi-Wing Orchestration Schema and Example
[generated] generated/generated-multi-wing-defensive-orchestration.schema.json
[generated] generated/generated-multi-wing-defensive-orchestration.example.yaml
[validate] Generated JSON Schema
[ok] JSON Schema syntax is valid: generated/generated-multi-wing-defensive-orchestration.schema.json
[validate] Generated Example
[ok] generated-multi-wing-defensive-orchestration.example.yaml is valid
[ok] generated handoff rules are internally valid
[ok] generated boundary escalation map is internally valid
```

### Next Direction

The next likely version is:

```text
v0.4 — Human Review Gate Expansion
```

Planned direction:

* generate explicit human review gates
* connect critical blocking conditions to review triggers
* generate approval record structures
* generate rejection record structures
* validate required human review paths
* strengthen release-readiness gating

---

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

