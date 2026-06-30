#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]

WING_DEFINITION_SCHEMA = ROOT / "schemas" / "wing-definition.schema.json"
WING_DEFINITION_EXAMPLE = ROOT / "examples" / "wing-definition.example.yaml"

GENERATED_SCHEMA = ROOT / "generated" / "generated-multi-wing-defensive-orchestration.schema.json"
GENERATED_EXAMPLE = ROOT / "generated" / "generated-multi-wing-defensive-orchestration.example.yaml"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at root: {path}")

    return data


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object at root: {path}")

    return data


def validate(instance: Dict[str, Any], schema: Dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    if errors:
        print(f"[error] {label} validation failed")

        for error in errors:
            path = ".".join(str(part) for part in error.path) or "<root>"
            print(f"  - path: {path}")
            print(f"    message: {error.message}")

        raise SystemExit(1)

    print(f"[ok] {label} is valid")


def check_json_schema_syntax(path: Path) -> None:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    print(f"[ok] JSON Schema syntax is valid: {path.relative_to(ROOT)}")


def validate_unique_wing_ids(definition: Dict[str, Any]) -> None:
    wings = definition["wings"]

    seen: Set[str] = set()
    duplicates: Set[str] = set()

    for wing in wings:
        wing_id = wing["wing_id"]

        if wing_id in seen:
            duplicates.add(wing_id)

        seen.add(wing_id)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        print(f"[error] duplicate wing_id detected: {duplicate_list}")
        raise SystemExit(1)

    print("[ok] wing_id values are unique")


def validate_handoff_references(definition: Dict[str, Any]) -> None:
    wings = definition["wings"]
    wing_ids = {wing["wing_id"] for wing in wings}

    invalid_refs: List[str] = []

    for wing in wings:
        from_wing = wing["wing_id"]

        for to_wing in wing.get("handoff_to", []):
            if to_wing not in wing_ids:
                invalid_refs.append(f"{from_wing} -> {to_wing}")

    if invalid_refs:
        print("[error] invalid handoff references detected")

        for ref in invalid_refs:
            print(f"  - {ref}")

        raise SystemExit(1)

    print("[ok] handoff references are valid")


def validate_unique_condition_ids(definition: Dict[str, Any]) -> None:
    wings = definition["wings"]

    seen: Set[str] = set()
    duplicates: Set[str] = set()

    for wing in wings:
        for condition in wing.get("blocking_conditions", []):
            condition_id = condition["condition_id"]

            if condition_id in seen:
                duplicates.add(condition_id)

            seen.add(condition_id)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        print(f"[error] duplicate condition_id detected: {duplicate_list}")
        raise SystemExit(1)

    print("[ok] condition_id values are unique")


def validate_blocking_condition_escalation_targets(definition: Dict[str, Any]) -> None:
    wings = definition["wings"]
    wing_ids = {wing["wing_id"] for wing in wings}

    invalid_targets: List[str] = []

    for wing in wings:
        for condition in wing.get("blocking_conditions", []):
            condition_id = condition["condition_id"]
            escalation_target = condition["escalation_target"]

            if escalation_target not in wing_ids:
                invalid_targets.append(f"{condition_id} -> {escalation_target}")

    if invalid_targets:
        print("[error] invalid blocking condition escalation targets detected")

        for target in invalid_targets:
            print(f"  - {target}")

        raise SystemExit(1)

    print("[ok] blocking condition escalation targets are valid")


def validate_blocking_condition_policy(definition: Dict[str, Any]) -> None:
    wings = definition["wings"]

    errors: List[str] = []

    for wing in wings:
        for condition in wing.get("blocking_conditions", []):
            condition_id = condition["condition_id"]
            severity = condition["severity"]
            requires_human_review = condition["requires_human_review"]
            trace_required = condition["trace_required"]

            if severity == "critical" and not requires_human_review:
                errors.append(
                    f"{condition_id}: critical severity must require human review"
                )

            if severity in {"high", "critical"} and not trace_required:
                errors.append(
                    f"{condition_id}: high or critical severity must require trace"
                )

    if errors:
        print("[error] invalid blocking condition policy")

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    print("[ok] blocking condition policy is valid")


def validate_generated_handoff_rules(generated_example: Dict[str, Any]) -> None:
    wing_ids = {wing["wing_id"] for wing in generated_example["wings"]}
    rule_ids: Set[str] = set()

    for rule in generated_example["handoff_rules"]:
        rule_id = rule["rule_id"]
        from_wing = rule["from_wing"]
        to_wing = rule["to_wing"]

        if rule_id in rule_ids:
            print(f"[error] duplicate generated handoff rule_id detected: {rule_id}")
            raise SystemExit(1)

        rule_ids.add(rule_id)

        if from_wing not in wing_ids:
            print(f"[error] generated handoff has invalid from_wing: {from_wing}")
            raise SystemExit(1)

        if to_wing not in wing_ids:
            print(f"[error] generated handoff has invalid to_wing: {to_wing}")
            raise SystemExit(1)

    print("[ok] generated handoff rules are internally valid")


def validate_generated_boundary_escalation_map(generated_example: Dict[str, Any]) -> None:
    wing_ids = {wing["wing_id"] for wing in generated_example["wings"]}
    condition_ids = {
        condition["condition_id"]
        for condition in generated_example["blocking_conditions"]
    }

    for item in generated_example["boundary_escalation_map"]:
        condition_id = item["condition_id"]
        source_wing = item["source_wing"]
        escalation_target = item["escalation_target"]

        if condition_id not in condition_ids:
            print(f"[error] escalation map references unknown condition_id: {condition_id}")
            raise SystemExit(1)

        if source_wing not in wing_ids:
            print(f"[error] escalation map references unknown source_wing: {source_wing}")
            raise SystemExit(1)

        if escalation_target not in wing_ids:
            print(f"[error] escalation map references unknown escalation_target: {escalation_target}")
            raise SystemExit(1)

    print("[ok] generated boundary escalation map is internally valid")


def validate_generated_human_review_gates(generated_example: Dict[str, Any]) -> None:
    wing_ids = {wing["wing_id"] for wing in generated_example["wings"]}
    condition_ids = {
        condition["condition_id"]
        for condition in generated_example["blocking_conditions"]
    }

    gate_ids: Set[str] = set()

    for gate in generated_example["human_review_gates"]:
        gate_id = gate["gate_id"]
        source_type = gate["source_type"]
        source_id = gate["source_id"]
        source_wing = gate["source_wing"]
        escalation_target = gate["escalation_target"]

        if gate_id in gate_ids:
            print(f"[error] duplicate human review gate_id detected: {gate_id}")
            raise SystemExit(1)

        gate_ids.add(gate_id)

        if source_wing not in wing_ids:
            print(f"[error] human review gate references unknown source_wing: {source_wing}")
            raise SystemExit(1)

        if escalation_target not in wing_ids:
            print(f"[error] human review gate references unknown escalation_target: {escalation_target}")
            raise SystemExit(1)

        if source_type == "wing" and source_id not in wing_ids:
            print(f"[error] human review gate references unknown wing source_id: {source_id}")
            raise SystemExit(1)

        if source_type == "blocking_condition" and source_id not in condition_ids:
            print(f"[error] human review gate references unknown condition source_id: {source_id}")
            raise SystemExit(1)

    print("[ok] generated human review gates are internally valid")


def validate_human_review_gate_coverage(generated_example: Dict[str, Any]) -> None:
    gate_sources = {
        (gate["source_type"], gate["source_id"])
        for gate in generated_example["human_review_gates"]
    }

    missing: List[str] = []

    for wing in generated_example["wings"]:
        if wing["requires_human_review"]:
            source = ("wing", wing["wing_id"])

            if source not in gate_sources:
                missing.append(f"wing:{wing['wing_id']}")

    for condition in generated_example["blocking_conditions"]:
        if condition["requires_human_review"]:
            source = ("blocking_condition", condition["condition_id"])

            if source not in gate_sources:
                missing.append(f"blocking_condition:{condition['condition_id']}")

    if missing:
        print("[error] missing human review gate coverage")

        for item in missing:
            print(f"  - {item}")

        raise SystemExit(1)

    print("[ok] human review gate coverage is complete")


def validate_review_record_templates(generated_example: Dict[str, Any]) -> None:
    templates = generated_example["review_record_templates"]

    for template_name in ["approval_record", "rejection_record"]:
        fields = templates[template_name]["required_fields"]

        if not fields:
            print(f"[error] {template_name} has no required fields")
            raise SystemExit(1)

        if "gate_id" not in fields:
            print(f"[error] {template_name} must include gate_id")
            raise SystemExit(1)

        if "trace_id" not in fields:
            print(f"[error] {template_name} must include trace_id")
            raise SystemExit(1)

        if "decision" not in fields:
            print(f"[error] {template_name} must include decision")
            raise SystemExit(1)

    print("[ok] review record templates are valid")


def validate_generated_trace_receipt_requirements(generated_example: Dict[str, Any]) -> None:
    wing_ids = {wing["wing_id"] for wing in generated_example["wings"]}
    handoff_rule_ids = {rule["rule_id"] for rule in generated_example["handoff_rules"]}
    condition_ids = {
        condition["condition_id"]
        for condition in generated_example["blocking_conditions"]
    }
    gate_ids = {
        gate["gate_id"]
        for gate in generated_example["human_review_gates"]
    }

    requirement_ids: Set[str] = set()

    for requirement in generated_example["trace_receipt_requirements"]:
        requirement_id = requirement["requirement_id"]
        target_type = requirement["target_type"]
        target_id = requirement["target_id"]
        source_wing = requirement["source_wing"]

        if requirement_id in requirement_ids:
            print(f"[error] duplicate trace requirement_id detected: {requirement_id}")
            raise SystemExit(1)

        requirement_ids.add(requirement_id)

        if source_wing not in wing_ids:
            print(f"[error] trace requirement references unknown source_wing: {source_wing}")
            raise SystemExit(1)

        if target_type == "wing" and target_id not in wing_ids:
            print(f"[error] trace requirement references unknown wing target_id: {target_id}")
            raise SystemExit(1)

        if target_type == "handoff_rule" and target_id not in handoff_rule_ids:
            print(f"[error] trace requirement references unknown handoff target_id: {target_id}")
            raise SystemExit(1)

        if target_type == "blocking_condition" and target_id not in condition_ids:
            print(f"[error] trace requirement references unknown condition target_id: {target_id}")
            raise SystemExit(1)

        if target_type == "human_review_gate" and target_id not in gate_ids:
            print(f"[error] trace requirement references unknown gate target_id: {target_id}")
            raise SystemExit(1)

    print("[ok] generated trace receipt requirements are internally valid")


def validate_trace_coverage_matrix(generated_example: Dict[str, Any]) -> None:
    requirement_ids = {
        requirement["requirement_id"]
        for requirement in generated_example["trace_receipt_requirements"]
    }

    covered_requirement_ids = {
        item["trace_requirement_id"]
        for item in generated_example["trace_coverage_matrix"]
        if item["covered"]
    }

    missing = requirement_ids - covered_requirement_ids

    if missing:
        print("[error] trace coverage matrix is missing requirements")

        for requirement_id in sorted(missing):
            print(f"  - {requirement_id}")

        raise SystemExit(1)

    print("[ok] trace coverage matrix covers all trace requirements")


def validate_required_trace_targets_have_requirements(generated_example: Dict[str, Any]) -> None:
    requirement_targets = {
        (requirement["target_type"], requirement["target_id"])
        for requirement in generated_example["trace_receipt_requirements"]
    }

    missing: List[str] = []

    for wing in generated_example["wings"]:
        if wing["emits_trace_receipt"]:
            target = ("wing", wing["wing_id"])

            if target not in requirement_targets:
                missing.append(f"wing:{wing['wing_id']}")

    for rule in generated_example["handoff_rules"]:
        target = ("handoff_rule", rule["rule_id"])

        if target not in requirement_targets:
            missing.append(f"handoff_rule:{rule['rule_id']}")

    for condition in generated_example["blocking_conditions"]:
        if condition["trace_required"]:
            target = ("blocking_condition", condition["condition_id"])

            if target not in requirement_targets:
                missing.append(f"blocking_condition:{condition['condition_id']}")

    for gate in generated_example["human_review_gates"]:
        if gate["trace_required"]:
            target = ("human_review_gate", gate["gate_id"])

            if target not in requirement_targets:
                missing.append(f"human_review_gate:{gate['gate_id']}")

    if missing:
        print("[error] required trace targets are missing trace requirements")

        for item in missing:
            print(f"  - {item}")

        raise SystemExit(1)

    print("[ok] required trace targets have trace requirements")


def run_generator() -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "generate_multi_wing_schema.py"),
        str(WING_DEFINITION_EXAMPLE)
    ]

    subprocess.run(cmd, check=True)


def main() -> None:
    print("[validate] Wing Definition")
    wing_schema = load_json(WING_DEFINITION_SCHEMA)
    wing_example = load_yaml(WING_DEFINITION_EXAMPLE)

    validate(wing_example, wing_schema, "wing-definition.example.yaml")
    validate_unique_wing_ids(wing_example)
    validate_handoff_references(wing_example)
    validate_unique_condition_ids(wing_example)
    validate_blocking_condition_escalation_targets(wing_example)
    validate_blocking_condition_policy(wing_example)

    print("[generate] Multi-Wing Orchestration Schema and Example")
    run_generator()

    print("[validate] Generated JSON Schema")
    check_json_schema_syntax(GENERATED_SCHEMA)

    print("[validate] Generated Example")
    generated_schema = load_json(GENERATED_SCHEMA)
    generated_example = load_yaml(GENERATED_EXAMPLE)

    validate(
        generated_example,
        generated_schema,
        "generated-multi-wing-defensive-orchestration.example.yaml"
    )

    validate_generated_handoff_rules(generated_example)
    validate_generated_boundary_escalation_map(generated_example)
    validate_generated_human_review_gates(generated_example)
    validate_human_review_gate_coverage(generated_example)
    validate_review_record_templates(generated_example)
    validate_generated_trace_receipt_requirements(generated_example)
    validate_trace_coverage_matrix(generated_example)
    validate_required_trace_targets_have_requirements(generated_example)


if __name__ == "__main__":
    main()
