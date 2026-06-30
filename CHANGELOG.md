# Changelog

## v0.4.0-candidate

### Added

* Added automatic `human_review_gates` generation.
* Added review gates for wings with `requires_human_review: true`.
* Added review gates for blocking conditions with `requires_human_review: true`.
* Added `review_record_templates` for approval and rejection records.
* Added validation for generated human review gates.
* Added validation for human review gate coverage.
* Added validation for approval and rejection record templates.

### Changed

* Updated `wing-definition.schema.json` from `0.3.0` to `0.4.0`.
* Added `approval_record_fields` and `rejection_record_fields` to `global_rules.human_review`.
* Updated generated orchestration examples to include `human_review_gates`.
* Updated generated orchestration examples to include `review_record_templates`.
* Strengthened CI validation around human review routing and review evidence.

### Purpose

v0.4 establishes the Human Review Gate Expansion layer.

This version turns `requires_human_review` from a boolean flag into a generated review gate structure.

```text
v0.1 Generator Seed Layer
= define and generate schema

v0.2 Handoff Rule Expansion
= generate and validate wing transitions

v0.3 Blocking Condition Expansion
= generate and validate defensive blocking routes

v0.4 Human Review Gate Expansion
= generate and validate human review gates
```

### Structural Position

The generator now checks whether required human review paths are explicitly generated.

A human review requirement is no longer only a boolean value.

It is now a generated gate with:

* a unique gate identity
* a source wing or blocking condition
* a review trigger
* an escalation target
* an approval record requirement
* a rejection record requirement
* a trace requirement

This prevents human review requirements from passing silently without review routing or evidence templates.

### Generated Artifacts

v0.4 generates:

```text
generated/generated-multi-wing-defensive-orchestration.schema.json
generated/generated-multi-wing-defensive-orchestration.example.yaml
```

The generated example now includes:

```text
blocking_conditions
boundary_escalation_map
human_review_gates
review_record_templates
```

### Validation Scope

v0.4 validates:

* source wing definition example
* duplicate `wing_id` values
* invalid `handoff_to` references
* duplicate `condition_id` values
* invalid blocking condition escalation targets
* blocking condition policy
* generated JSON Schema syntax
* generated example YAML against the generated schema
* generated handoff rule references
* generated boundary escalation map references
* generated human review gate references
* human review gate coverage
* review record template requirements

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
[ok] generated human review gates are internally valid
[ok] human review gate coverage is complete
[ok] review record templates are valid
```

### Next Direction

The next likely version is:

```text
v0.5 — Trace Receipt Bridge Expansion
```

Planned direction:

* generate trace receipt requirements per wing
* generate trace receipt requirements per handoff
* generate trace receipt requirements per blocking condition
* generate trace receipt requirements per human review gate
* connect review gates to trace receipts
* validate trace coverage before release-readiness checks

---

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
