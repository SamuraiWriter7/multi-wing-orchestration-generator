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


def validate_generated_handoff_rules(generated_example: Dict[str, Any]) -> None:
    wing_ids = {wing["wing_id"] for wing in generated_example["wings"]}

    for rule in generated_example["handoff_rules"]:
        from_wing = rule["from_wing"]
        to_wing = rule["to_wing"]

        if from_wing not in wing_ids:
            print(f"[error] generated handoff has invalid from_wing: {from_wing}")
            raise SystemExit(1)

        if to_wing not in wing_ids:
            print(f"[error] generated handoff has invalid to_wing: {to_wing}")
            raise SystemExit(1)

    print("[ok] generated handoff rules are internally valid")


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

    print("[generate] Multi-Wing Orchestration Schema and Example")
    run_generator()

    print("[validate] Generated JSON Schema")
    check_json_schema_syntax(GENERATED_SCHEMA)

    print("[validate] Generated Example")
    generated_schema = load_json(GENERATED_SCHEMA)
    generated_example = load_yaml(GENERATED_EXAMPLE)

    validate(generated_example, generated_schema, "generated-multi-wing-defensive-orchestration.example.yaml")
    validate_generated_handoff_rules(generated_example)


if __name__ == "__main__":
    main()
