# Multi-Wing Orchestration Generator

Experimental OS-level generator for defensive multi-wing orchestration structures, schema fragments, safety boundaries, escalation routes, and human review gates.

## Purpose

`multi-wing-orchestration-generator` is a generator layer for producing CI-verifiable Multi-Wing Orchestration schemas and examples from declarative wing definitions.

This repository begins as a separate generator arc after the first protocol arc of `Yin-Yang Mythos Regulator` was completed at v0.5.

The distinction is intentional:

```text
yin-yang-mythos-regulator
= defensive regulation protocol

multi-wing-orchestration-generator
= generator layer for producing defensive multi-wing structures
```

The goal is to keep the defensive protocol itself separate from the tooling that generates orchestration schemas, handoff rules, blocking routes, escalation maps, examples, and validation structures.

## v0.3 Scope

v0.3 defines the Blocking Condition Expansion layer.

It expands `blocking_conditions` from plain strings into structured defensive routing rules.

v0.3 adds:

* structured blocking condition definitions
* `condition_id`
* `description`
* `severity`
* `escalation_target`
* `requires_human_review`
* `trace_required`
* automatic `boundary_escalation_map` generation
* duplicate `condition_id` detection
* invalid `escalation_target` detection
* blocking condition policy validation
* generated boundary escalation map validation

## Repository Structure

```text
multi-wing-orchestration-generator/
├── README.md
├── CHANGELOG.md
├── schemas/
│   └── wing-definition.schema.json
├── examples/
│   └── wing-definition.example.yaml
├── generated/
│   └── .gitkeep
├── scripts/
│   ├── generate_multi_wing_schema.py
│   └── validate_examples.py
└── .github/
    └── workflows/
        └── validate.yml
```

## Generator Flow

```text
examples/wing-definition.example.yaml
        ↓
schemas/wing-definition.schema.json
        ↓
scripts/generate_multi_wing_schema.py
        ↓
generated/generated-multi-wing-defensive-orchestration.schema.json
generated/generated-multi-wing-defensive-orchestration.example.yaml
        ↓
scripts/validate_examples.py
        ↓
GitHub Actions
```

## Core Concepts

### Wing Definition

A wing definition declares each orchestration wing as a structured unit.

Each wing includes:

* `wing_id`
* `wing_name`
* `purpose`
* `allowed_outputs`
* `prohibited_outputs`
* `handoff_to`
* `blocking_conditions`
* `requires_human_review`
* `emits_trace_receipt`

### Handoff Rule Expansion

v0.2 introduced automatic expansion of each wing's `handoff_to` declarations into generated `handoff_rules`.

For example:

```yaml
wing_id: "finder"
handoff_to:
  - "analyst"
  - "boundary"
```

is expanded into generated handoff rules:

```yaml
handoff_rules:
  - from_wing: "finder"
    to_wing: "analyst"
    condition: "finder completed and analyst is eligible for next review step."
  - from_wing: "finder"
    to_wing: "boundary"
    condition: "finder completed and boundary is eligible for next review step."
```

This allows the generator to treat wing transitions as a verifiable orchestration graph instead of static prose.

### Blocking Condition Expansion

v0.3 expands `blocking_conditions` from plain strings into structured defensive routing rules.

Before v0.3:

```yaml
blocking_conditions:
  - "Schema validation fails."
  - "Required receipt fields are missing."
```

From v0.3 onward:

```yaml
blocking_conditions:
  - condition_id: "verifier.schema_validation_fails"
    description: "Schema validation fails."
    severity: "high"
    escalation_target: "human_gate"
    requires_human_review: true
    trace_required: true
```

Each blocking condition now includes:

* `condition_id`
* `description`
* `severity`
* `escalation_target`
* `requires_human_review`
* `trace_required`

This turns blocking conditions into explicit defensive routing rules.

### Boundary Escalation Map

v0.3 automatically generates a `boundary_escalation_map` from declared blocking conditions.

The escalation map records:

* the blocking condition ID
* the source wing
* the severity level
* the escalation target
* whether human review is required
* whether trace evidence is required

This allows defensive routes to be validated as part of CI.

### Wing Graph Validation

The generator and validation script check:

* whether every `wing_id` is unique
* whether every `handoff_to` target exists
* whether generated `handoff_rules` reference valid wings
* whether the generated example validates against the generated schema

This prevents silent orchestration drift caused by broken wing references.

### Blocking Condition Validation

v0.3 adds validation for defensive blocking policy.

The validation script checks:

* whether every `condition_id` is unique
* whether every `escalation_target` exists as a valid wing
* whether every `critical` condition requires human review
* whether every `high` or `critical` condition requires trace evidence
* whether the generated `boundary_escalation_map` references valid wings and conditions

This prevents unsafe or incomplete blocking routes from passing silently.

### Global Rules

Global rules define shared orchestration requirements:

* safety boundaries
* human review requirements
* trace receipt requirements
* orchestration receipt requirements

### Generated Schema

The generated schema includes:

* `schema_version`
* `orchestration_id`
* `created_at`
* `wings`
* `handoff_rules`
* `blocking_conditions`
* `boundary_escalation_map`
* `safety_boundary`
* `human_review`
* `trace_core`

### Generated Example

When `include_generated_example` is enabled, the generator also produces:

```text
generated/generated-multi-wing-defensive-orchestration.example.yaml
```

This example is validated against the generated JSON Schema in CI.

## Usage

Install dependencies:

```bash
pip install pyyaml jsonschema
```

Generate schema and example:

```bash
python scripts/generate_multi_wing_schema.py examples/wing-definition.example.yaml
```

Validate examples and generated artifacts:

```bash
python scripts/validate_examples.py
```

## Expected Validation Output

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

## Version Arc

```text
v0.1 Generator Seed Layer
v0.2 Handoff Rule Expansion
v0.3 Blocking Condition Expansion
```

### v0.1 — Generator Seed Layer

v0.1 introduced the first generator seed layer.

It established the minimum path from declarative wing definitions to a generated CI-verifiable JSON Schema.

### v0.2 — Handoff Rule Expansion

v0.2 expanded the generator from schema output into wing graph generation.

It added automatic handoff expansion, generated examples, reference validation, and stronger CI checks.

The generator became able to verify that declared wing transitions form a valid orchestration graph.

### v0.3 — Blocking Condition Expansion

v0.3 expands blocking conditions into structured defensive routing rules.

It adds severity, escalation targets, human review requirements, trace requirements, and generated boundary escalation maps.

The generator now verifies that defensive stopping conditions are not just declared, but structurally routable.

## Relationship to Yin-Yang Mythos Regulator

`Yin-Yang Mythos Regulator` closes its first protocol arc at v0.5.

```text
v0.1 Furnace    Mythos Regulation Record
v0.2 Cycle      Defensive Repair Loop
v0.3 Boundary   Agent Permission Boundary
v0.4 Wind Path  Trace Receipt Bridge
v0.5 Wings      Multi-Wing Defensive Orchestration
```

That repository defines the defensive regulation protocol.

This repository begins the next arc as a generator layer.

```text
Yin-Yang Mythos Regulator
= the defensive regulation protocol itself

Multi-Wing Orchestration Generator
= the forge that generates defensive orchestration structures
```

## Future Direction

The next likely version is:

```text
v0.4 — Human Review Gate Expansion
```

Potential future layers include:

* generated human review gates
* approval record generation
* rejection record generation
* review trigger expansion
* required review path validation
* trace receipt bridge generation
* generated CI helper files
* generated repository bootstrap templates
* orchestration graph visualization
* Multi-Wing release-readiness checks

## Summary

`multi-wing-orchestration-generator` turns Multi-Wing orchestration from a manually written protocol pattern into a generator-driven OS layer.

v0.1 created the generator seed.

v0.2 gave that seed a wing graph.

v0.3 gives the graph defensive stopping routes.

This repository is becoming a defensive orchestration forge.


