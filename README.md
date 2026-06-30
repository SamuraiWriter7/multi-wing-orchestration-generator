# Multi-Wing Orchestration Generator

Experimental OS-level generator for defensive multi-wing orchestration structures, schema fragments, safety boundaries, and human review gates.

## Purpose

`multi-wing-orchestration-generator` is a generator layer for producing CI-verifiable Multi-Wing Orchestration schemas from declarative wing definitions.

It is designed as a separate repository from `yin-yang-mythos-regulator`.

The distinction is intentional:

```text
yin-yang-mythos-regulator
= defensive regulation protocol

multi-wing-orchestration-generator
= generator layer for producing defensive multi-wing structures

v0.1 Scope

v0.1 defines the first generator seed layer.

It introduces:

wing-definition.schema.json
wing-definition.example.yaml
generate_multi_wing_schema.py
validate_examples.py
GitHub Actions validation workflow
Generator Flow
examples/wing-definition.example.yaml
        ↓
schemas/wing-definition.schema.json
        ↓
scripts/generate_multi_wing_schema.py
        ↓
generated/generated-multi-wing-defensive-orchestration.schema.json
        ↓
scripts/validate_examples.py
        ↓
GitHub Actions
Core Concepts
Wing Definition

A wing definition declares:

wing_id
wing_name
purpose
allowed_outputs
prohibited_outputs
handoff_to
blocking_conditions
requires_human_review
emits_trace_receipt
Global Rules

Global rules define:

safety boundaries
human review requirements
trace receipt requirements
orchestration receipt requirements
Generated Schema

The generated schema includes:

schema version
orchestration ID
wing states
handoff rules
blocking conditions
safety boundary
human review gate
trace core
Usage

Install dependencies:

pip install pyyaml jsonschema

Generate schema:

python scripts/generate_multi_wing_schema.py examples/wing-definition.example.yaml

Validate:

python scripts/validate_examples.py
Version Arc
v0.1 Generator Seed Layer

Future versions may add:

generated example YAML
handoff rule expansion
blocking condition expansion
safety boundary templates
human review gate templates
trace receipt bridge generation
CI helper generation
repository bootstrap generation
Relationship to Yin-Yang Mythos Regulator

Yin-Yang Mythos Regulator closes its first protocol arc at v0.5.

This repository begins the next arc as a generator layer.

The goal is to avoid mixing the defensive regulation protocol itself with schema-generation tooling.
