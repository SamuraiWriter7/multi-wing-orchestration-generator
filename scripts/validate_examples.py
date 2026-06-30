#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]

WING_DEFINITION_SCHEMA = ROOT / "schemas" / "wing-definition.schema.json"
WING_DEFINITION_EXAMPLE = ROOT / "examples" / "wing-definition.example.yaml"
GENERATED_SCHEMA = ROOT / "generated" / "generated-multi-wing-defensive-orchestration.schema.json"


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

    print("[generate] Multi-Wing Orchestration Schema")
    run_generator()

    print("[validate] Generated JSON Schema")
    check_json_schema_syntax(GENERATED_SCHEMA)


if __name__ == "__main__":
    main()
