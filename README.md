# Multi-Wing Orchestration Generator

Experimental OS-level generator for defensive multi-wing orchestration structures, schema fragments, handoff rules, blocking routes, escalation maps, human review gates, review record templates, trace receipt requirements, and trace coverage validation.

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

The goal is to keep the defensive protocol itself separate from the tooling that generates orchestration schemas, handoff rules, blocking routes, escalation maps, human review gates, review record templates, trace receipt requirements, examples, and validation structures.

## v0.5 Scope

v0.5 defines the Trace Receipt Bridge Expansion layer.

It expands traceability from a global setting into generated `trace_receipt_requirements` and a generated `trace_coverage_matrix`.

v0.5 adds:

* automatic `trace_receipt_requirements` generation
* trace requirements for wings that emit trace receipts
* trace requirements for generated handoff rules
* trace requirements for blocking conditions that require trace evidence
* trace requirements for human review gates that require trace evidence
* `trace_coverage_matrix`
* validation for generated trace receipt requirements
* validation for trace coverage completeness
* validation that required trace targets have trace requirements

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
  - rule_id: "handoff.finder.analyst"
    from_wing: "finder"
    to_wing: "analyst"
    condition: "finder completed and analyst is eligible for next review step."
  - rule_id: "handoff.finder.boundary"
    from_wing: "finder"
    to_wing: "boundary"
    condition: "finder completed and boundary is eligible for next review step."
```

This allows the generator to treat wing transitions as a verifiable orchestration graph instead of static prose.

### Blocking Condition Expansion

v0.3 expanded `blocking_conditions` from plain strings into structured defensive routing rules.

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

Each blocking condition includes:

* `condition_id`
* `description`
* `severity`
* `escalation_target`
* `requires_human_review`
* `trace_required`

This turns blocking conditions into explicit defensive routing rules.

### Boundary Escalation Map

v0.3 introduced automatic `boundary_escalation_map` generation from declared blocking conditions.

The escalation map records:

* the blocking condition ID
* the source wing
* the severity level
* the escalation target
* whether human review is required
* whether trace evidence is required

This allows defensive routes to be validated as part of CI.

### Human Review Gate Expansion

v0.4 expanded `requires_human_review` into generated `human_review_gates`.

The generator creates review gates from:

* wings that require human review
* blocking conditions that require human review

For example, a blocking condition such as:

```yaml
- condition_id: "repair.increases_operational_risk"
  description: "Repair path increases operational risk."
  severity: "high"
  escalation_target: "human_gate"
  requires_human_review: true
  trace_required: true
```

can produce a generated human review gate:

```yaml
human_review_gates:
  - gate_id: "gate.repair.increases_operational_risk"
    source_type: "blocking_condition"
    source_id: "repair.increases_operational_risk"
    source_wing: "repair"
    severity: "high"
    reviewer_role: "authorized_human_reviewer"
    review_trigger: "Repair path increases operational risk."
    escalation_target: "human_gate"
    approval_record_required: true
    rejection_record_required: true
    trace_required: true
```

Each generated human review gate includes:

* `gate_id`
* `source_type`
* `source_id`
* `source_wing`
* `severity`
* `reviewer_role`
* `review_trigger`
* `escalation_target`
* `approval_record_required`
* `rejection_record_required`
* `trace_required`

This turns human review from a passive flag into an explicit review gate.

### Review Record Templates

v0.4 introduced `review_record_templates`.

These templates define the required fields for approval and rejection records.

Example:

```yaml
review_record_templates:
  approval_record:
    required_fields:
      - "review_id"
      - "gate_id"
      - "reviewer_role"
      - "decision"
      - "approved_at"
      - "approval_reason"
      - "trace_id"
  rejection_record:
    required_fields:
      - "review_id"
      - "gate_id"
      - "reviewer_role"
      - "decision"
      - "rejected_at"
      - "rejection_reason"
      - "trace_id"
```

This ensures that human decisions are not only required, but also traceable.

### Trace Receipt Bridge Expansion

v0.5 expands traceability into generated `trace_receipt_requirements`.

The generator creates trace receipt requirements for:

* wings that emit trace receipts
* generated handoff rules
* blocking conditions that require trace evidence
* human review gates that require trace evidence

Example:

```yaml
trace_receipt_requirements:
  - requirement_id: "trace.wing.finder"
    target_type: "wing"
    target_id: "finder"
    source_wing: "finder"
    event_type: "wing_event"
    required_fields:
      - "trace_id"
      - "wing_id"
      - "event_type"
      - "input_reference"
      - "output_reference"
      - "created_at"
    required: true
```

This turns traceability from a global setting into a generated, target-specific structure.

### Trace Coverage Matrix

v0.5 also introduces `trace_coverage_matrix`.

The trace coverage matrix verifies that every trace-required target has a corresponding trace receipt requirement.

Example:

```yaml
trace_coverage_matrix:
  - coverage_id: "coverage.wing.finder"
    target_type: "wing"
    target_id: "finder"
    trace_requirement_id: "trace.wing.finder"
    covered: true
```

This allows CI to detect missing trace coverage before release.

### Wing Graph Validation

The generator and validation script check:

* whether every `wing_id` is unique
* whether every `handoff_to` target exists
* whether generated `handoff_rules` reference valid wings
* whether generated handoff rule IDs are unique
* whether the generated example validates against the generated schema

This prevents silent orchestration drift caused by broken wing references.

### Blocking Condition Validation

The validation script checks:

* whether every `condition_id` is unique
* whether every `escalation_target` exists as a valid wing
* whether every `critical` condition requires human review
* whether every `high` or `critical` condition requires trace evidence
* whether the generated `boundary_escalation_map` references valid wings and conditions

This prevents unsafe or incomplete blocking routes from passing silently.

### Human Review Gate Validation

The validation script checks:

* whether generated human review gates reference valid wings
* whether generated human review gates reference valid blocking conditions
* whether generated human review gates have unique `gate_id` values
* whether every human-review-required wing has a corresponding gate
* whether every human-review-required blocking condition has a corresponding gate
* whether approval and rejection record templates include required evidence fields

This prevents human review requirements from existing only as decorative flags.

### Trace Coverage Validation

v0.5 adds validation for trace receipt coverage.

The validation script checks:

* whether generated trace receipt requirements reference valid wings
* whether generated trace receipt requirements reference valid handoff rules
* whether generated trace receipt requirements reference valid blocking conditions
* whether generated trace receipt requirements reference valid human review gates
* whether every trace requirement is covered by the trace coverage matrix
* whether every trace-required wing, handoff, blocking condition, and human review gate has a trace requirement

This prevents trace requirements from remaining only as global policy text.

### Global Rules

Global rules define shared orchestration requirements:

* safety boundaries
* human review requirements
* approval record fields
* rejection record fields
* trace receipt requirements
* required trace event types
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
* `human_review_gates`
* `review_record_templates`
* `trace_receipt_requirements`
* `trace_coverage_matrix`
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
[ok] generated human review gates are internally valid
[ok] human review gate coverage is complete
[ok] review record templates are valid
[ok] generated trace receipt requirements are internally valid
[ok] trace coverage matrix covers all trace requirements
[ok] required trace targets have trace requirements
```

## Version Arc

```text
v0.1 Generator Seed Layer
v0.2 Handoff Rule Expansion
v0.3 Blocking Condition Expansion
v0.4 Human Review Gate Expansion
v0.5 Trace Receipt Bridge Expansion
```

### v0.1 — Generator Seed Layer

v0.1 introduced the first generator seed layer.

It established the minimum path from declarative wing definitions to a generated CI-verifiable JSON Schema.

### v0.2 — Handoff Rule Expansion

v0.2 expanded the generator from schema output into wing graph generation.

It added automatic handoff expansion, generated examples, reference validation, and stronger CI checks.

The generator became able to verify that declared wing transitions form a valid orchestration graph.

### v0.3 — Blocking Condition Expansion

v0.3 expanded blocking conditions into structured defensive routing rules.

It added severity, escalation targets, human review requirements, trace requirements, and generated boundary escalation maps.

The generator became able to verify that defensive stopping conditions are not just declared, but structurally routable.

### v0.4 — Human Review Gate Expansion

v0.4 expanded human review flags into generated review gates.

It added human review gate generation, approval record templates, rejection record templates, gate coverage validation, and review evidence validation.

The generator became able to verify that required human review paths are explicitly generated and traceable.

### v0.5 — Trace Receipt Bridge Expansion

v0.5 expands traceability into generated trace receipt requirements and trace coverage validation.

It adds target-specific trace requirements, trace coverage matrices, and CI checks for missing trace coverage.

The generator now verifies that trace-required events are explicitly covered before release.

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

## First Arc Completion

The first generator arc can be considered complete at v0.5.

```text
v0.1
Generate

v0.2
Connect

v0.3
Block

v0.4
Review

v0.5
Trace
```

At this point, the generator can produce a CI-verifiable defensive orchestration structure with:

* wing definitions
* handoff rules
* blocking conditions
* boundary escalation maps
* human review gates
* review record templates
* trace receipt requirements
* trace coverage matrices

## Future Direction

Future versions may proceed into a second generator arc.

Possible next direction:

```text
v0.6 — Release Readiness Gate Generator
```

Potential future layers include:

* generated release-readiness gates
* generated candidate release checklists
* README / CHANGELOG alignment checks
* schema / example alignment checks
* CI helper generation
* repository bootstrap templates
* orchestration graph visualization
* Multi-Wing release-readiness reports

If the scope expands significantly, future tooling may also be split into related repositories to keep this generator focused.

## Summary

`multi-wing-orchestration-generator` turns Multi-Wing orchestration from a manually written protocol pattern into a generator-driven OS layer.

v0.1 created the generator seed.

v0.2 gave that seed a wing graph.

v0.3 gave the graph defensive stopping routes.

v0.4 gave the routes human review gates and decision records.

v0.5 gives the entire structure trace receipt requirements and trace coverage validation.

This repository is now a defensive orchestration forge with traceable output.



