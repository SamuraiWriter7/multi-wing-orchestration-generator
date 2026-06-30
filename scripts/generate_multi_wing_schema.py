#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object at root: {path}")

    return data


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True
        )


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_wing_ids(wings: List[Dict[str, Any]]) -> List[str]:
    return [wing["wing_id"] for wing in wings]


def validate_unique_wing_ids(wings: List[Dict[str, Any]]) -> None:
    seen: Set[str] = set()
    duplicates: Set[str] = set()

    for wing in wings:
        wing_id = wing["wing_id"]

        if wing_id in seen:
            duplicates.add(wing_id)

        seen.add(wing_id)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate wing_id detected: {duplicate_list}")


def validate_handoff_references(wings: List[Dict[str, Any]]) -> None:
    wing_ids = set(get_wing_ids(wings))
    errors: List[str] = []

    for wing in wings:
        from_wing = wing["wing_id"]

        for to_wing in wing.get("handoff_to", []):
            if to_wing not in wing_ids:
                errors.append(f"{from_wing} -> {to_wing}")

    if errors:
        joined = "\n  - ".join(errors)
        raise ValueError(f"Invalid handoff reference detected:\n  - {joined}")


def validate_unique_condition_ids(wings: List[Dict[str, Any]]) -> None:
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
        raise ValueError(f"Duplicate condition_id detected: {duplicate_list}")


def validate_blocking_condition_escalation_targets(wings: List[Dict[str, Any]]) -> None:
    wing_ids = set(get_wing_ids(wings))
    errors: List[str] = []

    for wing in wings:
        for condition in wing.get("blocking_conditions", []):
            condition_id = condition["condition_id"]
            escalation_target = condition["escalation_target"]

            if escalation_target not in wing_ids:
                errors.append(f"{condition_id} -> {escalation_target}")

    if errors:
        joined = "\n  - ".join(errors)
        raise ValueError(f"Invalid escalation_target detected:\n  - {joined}")


def validate_blocking_condition_policy(wings: List[Dict[str, Any]]) -> None:
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
        joined = "\n  - ".join(errors)
        raise ValueError(f"Invalid blocking condition policy:\n  - {joined}")


def validate_definition_integrity(wings: List[Dict[str, Any]]) -> None:
    validate_unique_wing_ids(wings)
    validate_handoff_references(wings)
    validate_unique_condition_ids(wings)
    validate_blocking_condition_escalation_targets(wings)
    validate_blocking_condition_policy(wings)


def expand_handoff_rules(wings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    handoff_rules: List[Dict[str, str]] = []

    for wing in wings:
        from_wing = wing["wing_id"]

        for to_wing in wing.get("handoff_to", []):
            handoff_rules.append(
                {
                    "from_wing": from_wing,
                    "to_wing": to_wing,
                    "condition": f"{from_wing} completed and {to_wing} is eligible for next review step."
                }
            )

    return handoff_rules


def expand_blocking_conditions(wings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    blocking_conditions: List[Dict[str, Any]] = []

    for wing in wings:
        wing_id = wing["wing_id"]

        for condition in wing.get("blocking_conditions", []):
            blocking_conditions.append(
                {
                    "condition_id": condition["condition_id"],
                    "wing_id": wing_id,
                    "description": condition["description"],
                    "severity": condition["severity"],
                    "escalation_target": condition["escalation_target"],
                    "requires_human_review": condition["requires_human_review"],
                    "trace_required": condition["trace_required"]
                }
            )

    return blocking_conditions


def build_boundary_escalation_map(wings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    escalation_map: List[Dict[str, Any]] = []

    for wing in wings:
        source_wing = wing["wing_id"]

        for condition in wing.get("blocking_conditions", []):
            escalation_map.append(
                {
                    "condition_id": condition["condition_id"],
                    "source_wing": source_wing,
                    "severity": condition["severity"],
                    "escalation_target": condition["escalation_target"],
                    "requires_human_review": condition["requires_human_review"],
                    "trace_required": condition["trace_required"]
                }
            )

    return escalation_map


def build_generated_schema(definition: Dict[str, Any]) -> Dict[str, Any]:
    target = definition["target"]
    wings = definition["wings"]
    strict = definition["generator_config"]["strict_additional_properties"]

    validate_definition_integrity(wings)

    wing_ids = get_wing_ids(wings)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": target["output_schema_id"],
        "title": target["output_schema_title"],
        "description": "Generated Multi-Wing Defensive Orchestration schema.",
        "type": "object",
        "additionalProperties": not strict,
        "required": [
            "schema_version",
            "orchestration_id",
            "created_at",
            "wings",
            "handoff_rules",
            "blocking_conditions",
            "boundary_escalation_map",
            "safety_boundary",
            "human_review",
            "trace_core"
        ],
        "properties": {
            "schema_version": {
                "type": "string",
                "const": "0.3.0"
            },
            "orchestration_id": {
                "type": "string",
                "minLength": 1
            },
            "created_at": {
                "type": "string",
                "format": "date-time"
            },
            "wings": {
                "type": "array",
                "minItems": len(wings),
                "items": {
                    "$ref": "#/$defs/wing_state"
                }
            },
            "handoff_rules": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/handoff_rule"
                }
            },
            "blocking_conditions": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/blocking_condition"
                }
            },
            "boundary_escalation_map": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/boundary_escalation"
                }
            },
            "safety_boundary": {
                "$ref": "#/$defs/safety_boundary"
            },
            "human_review": {
                "$ref": "#/$defs/human_review"
            },
            "trace_core": {
                "$ref": "#/$defs/trace_core"
            }
        },
        "$defs": {
            "wing_id": {
                "type": "string",
                "enum": wing_ids
            },
            "severity": {
                "type": "string",
                "enum": [
                    "low",
                    "medium",
                    "high",
                    "critical"
                ]
            },
            "wing_state": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "wing_id",
                    "status",
                    "allowed_outputs",
                    "prohibited_outputs",
                    "requires_human_review",
                    "emits_trace_receipt"
                ],
                "properties": {
                    "wing_id": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "idle",
                            "active",
                            "blocked",
                            "completed",
                            "escalated"
                        ]
                    },
                    "allowed_outputs": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "prohibited_outputs": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "requires_human_review": {
                        "type": "boolean"
                    },
                    "emits_trace_receipt": {
                        "type": "boolean"
                    }
                }
            },
            "handoff_rule": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "from_wing",
                    "to_wing",
                    "condition"
                ],
                "properties": {
                    "from_wing": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "to_wing": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "condition": {
                        "type": "string",
                        "minLength": 1
                    }
                }
            },
            "blocking_condition": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "condition_id",
                    "wing_id",
                    "description",
                    "severity",
                    "escalation_target",
                    "requires_human_review",
                    "trace_required"
                ],
                "properties": {
                    "condition_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "wing_id": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "description": {
                        "type": "string",
                        "minLength": 1
                    },
                    "severity": {
                        "$ref": "#/$defs/severity"
                    },
                    "escalation_target": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "requires_human_review": {
                        "type": "boolean"
                    },
                    "trace_required": {
                        "type": "boolean"
                    }
                }
            },
            "boundary_escalation": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "condition_id",
                    "source_wing",
                    "severity",
                    "escalation_target",
                    "requires_human_review",
                    "trace_required"
                ],
                "properties": {
                    "condition_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "source_wing": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "severity": {
                        "$ref": "#/$defs/severity"
                    },
                    "escalation_target": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "requires_human_review": {
                        "type": "boolean"
                    },
                    "trace_required": {
                        "type": "boolean"
                    }
                }
            },
            "safety_boundary": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "prohibited_uses",
                    "escalation_conditions"
                ],
                "properties": {
                    "prohibited_uses": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "escalation_conditions": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    }
                }
            },
            "human_review": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "required",
                    "reviewer_role",
                    "review_triggers"
                ],
                "properties": {
                    "required": {
                        "type": "boolean"
                    },
                    "reviewer_role": {
                        "type": "string",
                        "minLength": 1
                    },
                    "review_triggers": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    }
                }
            },
            "trace_core": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "enabled",
                    "required_trace_fields",
                    "required_orchestration_fields"
                ],
                "properties": {
                    "enabled": {
                        "type": "boolean"
                    },
                    "required_trace_fields": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "required_orchestration_fields": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }


def build_generated_example(definition: Dict[str, Any]) -> Dict[str, Any]:
    wings = definition["wings"]
    global_rules = definition["global_rules"]

    validate_definition_integrity(wings)

    return {
        "schema_version": "0.3.0",
        "orchestration_id": f"{definition['target']['protocol_name']}.generated.example",
        "created_at": now_utc(),
        "wings": [
            {
                "wing_id": wing["wing_id"],
                "status": "idle",
                "allowed_outputs": wing["allowed_outputs"],
                "prohibited_outputs": wing["prohibited_outputs"],
                "requires_human_review": wing["requires_human_review"],
                "emits_trace_receipt": wing["emits_trace_receipt"]
            }
            for wing in wings
        ],
        "handoff_rules": expand_handoff_rules(wings),
        "blocking_conditions": expand_blocking_conditions(wings),
        "boundary_escalation_map": build_boundary_escalation_map(wings),
        "safety_boundary": {
            "prohibited_uses": global_rules["safety_boundary"]["prohibited_uses"],
            "escalation_conditions": global_rules["safety_boundary"]["escalation_conditions"]
        },
        "human_review": {
            "required": global_rules["human_review"]["required"],
            "reviewer_role": global_rules["human_review"]["reviewer_role"],
            "review_triggers": global_rules["human_review"]["review_triggers"]
        },
        "trace_core": {
            "enabled": global_rules["trace_receipt"]["enabled"],
            "required_trace_fields": global_rules["trace_receipt"]["required_fields"],
            "required_orchestration_fields": global_rules["orchestration_receipt"]["required_fields"]
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Multi-Wing Orchestration schema and example from a wing definition YAML."
    )
    parser.add_argument(
        "definition",
        type=Path,
        help="Path to wing-definition YAML."
    )
    parser.add_argument(
        "--schema-output",
        type=Path,
        default=None,
        help="Optional output path for generated JSON Schema."
    )
    parser.add_argument(
        "--example-output",
        type=Path,
        default=None,
        help="Optional output path for generated example YAML."
    )

    args = parser.parse_args()

    definition = load_yaml(args.definition)

    output_directory = Path(definition["generator_config"]["output_directory"])
    schema_filename = definition["target"]["output_schema_filename"]
    example_filename = definition["target"]["output_example_filename"]

    schema_output = args.schema_output or output_directory / schema_filename
    example_output = args.example_output or output_directory / example_filename

    generated_schema = build_generated_schema(definition)
    write_json(schema_output, generated_schema)
    print(f"[generated] {schema_output}")

    if definition["generator_config"]["include_generated_example"]:
        generated_example = build_generated_example(definition)
        write_yaml(example_output, generated_example)
        print(f"[generated] {example_output}")


if __name__ == "__main__":
    main()
