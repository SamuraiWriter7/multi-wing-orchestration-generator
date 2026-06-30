# Multi-Wing Orchestration Generator

Experimental OS-level generator for defensive multi-wing orchestration structures, schema fragments, safety boundaries, and human review gates.

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

The goal is to keep the defensive protocol itself separate from the tooling that generates orchestration schemas, handoff rules, examples, and validation structures.

## v0.2 Scope

v0.2 defines the Handoff Rule Expansion layer.

It expands the generator from simple schema output into wing graph generation and validation.

v0.2 adds:

* automatic `handoff_rules` generation from each wing's `handoff_to` declarations
* duplicate `wing_id` detection
* invalid handoff reference detection
* generated orchestration example YAML output
* validation of generated examples against generated schemas
* internal validation of generated handoff rules
* stronger CI checks for wing graph consistency

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

v0.2 automatically expands each wing's `handoff_to` declarations into generated `handoff_rules`.

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

### Wing Graph Validation

The generator and validation script check:

* whether every `wing_id` is unique
* whether every `handoff_to` target exists
* whether generated `handoff_rules` reference valid wings
* whether the generated example validates against the generated schema

This prevents silent orchestration drift caused by broken wing references.

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
[generate] Multi-Wing Orchestration Schema and Example
[generated] generated/generated-multi-wing-defensive-orchestration.schema.json
[generated] generated/generated-multi-wing-defensive-orchestration.example.yaml
[validate] Generated JSON Schema
[ok] JSON Schema syntax is valid: generated/generated-multi-wing-defensive-orchestration.schema.json
[validate] Generated Example
[ok] generated-multi-wing-defensive-orchestration.example.yaml is valid
[ok] generated handoff rules are internally valid
```

## Version Arc

```text
v0.1 Generator Seed Layer
v0.2 Handoff Rule Expansion
```

### v0.1 — Generator Seed Layer

v0.1 introduced the first generator seed layer.

It established the minimum path from declarative wing definitions to a generated CI-verifiable JSON Schema.

### v0.2 — Handoff Rule Expansion

v0.2 expands the generator from schema output into wing graph generation.

It adds automatic handoff expansion, generated examples, reference validation, and stronger CI checks.

The generator now verifies that declared wing transitions form a valid orchestration graph.

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
v0.3 — Blocking Condition Expansion
```

Potential future layers include:

* blocking condition severity classification
* boundary escalation maps
* human review gate expansion
* trace receipt bridge generation
* generated CI helper files
* generated repository bootstrap templates
* orchestration graph visualization
* Multi-Wing release-readiness checks

## Summary

`multi-wing-orchestration-generator` turns Multi-Wing orchestration from a manually written protocol pattern into a generator-driven OS layer.

v0.1 created the generator seed.

v0.2 gives that seed a wing graph.

This repository is the beginning of a defensive orchestration forge.

