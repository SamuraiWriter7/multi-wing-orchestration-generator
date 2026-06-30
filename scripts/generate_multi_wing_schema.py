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
                    "rule_id": f"handoff.{from_wing}.{to_wing}",
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


def build_human_review_gates(
    wings: List[Dict[str, Any]],
    reviewer_role: str
) -> List[Dict[str, Any]]:
    gates: List[Dict[str, Any]] = []
    wing_ids = set(get_wing_ids(wings))
    default_escalation_target = "human_gate" if "human_gate" in wing_ids else wings[0]["wing_id"]

    for wing in wings:
        wing_id = wing["wing_id"]

        if wing["requires_human_review"]:
            gates.append(
                {
                    "gate_id": f"gate.{wing_id}.wing_review",
                    "source_type": "wing",
                    "source_id": wing_id,
                    "source_wing": wing_id,
                    "severity": "medium",
                    "reviewer_role": reviewer_role,
                    "review_trigger": f"{wing_id} requires human review before completion.",
                    "escalation_target": default_escalation_target,
                    "approval_record_required": True,
                    "rejection_record_required": True,
                    "trace_required": wing["emits_trace_receipt"]
                }
            )

        for condition in wing.get("blocking_conditions", []):
            if condition["requires_human_review"]:
                gates.append(
                    {
                        "gate_id": f"gate.{condition['condition_id']}",
                        "source_type": "blocking_condition",
                        "source_id": condition["condition_id"],
                        "source_wing": wing_id,
                        "severity": condition["severity"],
                        "reviewer_role": reviewer_role,
                        "review_trigger": condition["description"],
                        "escalation_target": condition["escalation_target"],
                        "approval_record_required": True,
                        "rejection_record_required": True,
                        "trace_required": condition["trace_required"]
                    }
                )

    return gates


def build_review_record_templates(global_rules: Dict[str, Any]) -> Dict[str, Any]:
    human_review = global_rules["human_review"]

    return {
        "approval_record": {
            "required_fields": human_review["approval_record_fields"]
        },
        "rejection_record": {
            "required_fields": human_review["rejection_record_fields"]
        }
    }


def build_trace_receipt_requirements(
    wings: List[Dict[str, Any]],
    handoff_rules: List[Dict[str, Any]],
    blocking_conditions: List[Dict[str, Any]],
    human_review_gates: List[Dict[str, Any]],
    required_fields: List[str]
) -> List[Dict[str, Any]]:
    requirements: List[Dict[str, Any]] = []

    for wing in wings:
        if wing["emits_trace_receipt"]:
            wing_id = wing["wing_id"]

            requirements.append(
                {
                    "requirement_id": f"trace.wing.{wing_id}",
                    "target_type": "wing",
                    "target_id": wing_id,
                    "source_wing": wing_id,
                    "event_type": "wing_event",
                    "required_fields": required_fields,
                    "required": True
                }
            )

    for rule in handoff_rules:
        requirements.append(
            {
                "requirement_id": f"trace.{rule['rule_id']}",
                "target_type": "handoff_rule",
                "target_id": rule["rule_id"],
                "source_wing": rule["from_wing"],
                "event_type": "handoff_event",
                "required_fields": required_fields,
                "required": True
            }
        )

    for condition in blocking_conditions:
        if condition["trace_required"]:
            requirements.append(
                {
                    "requirement_id": f"trace.blocking_condition.{condition['condition_id']}",
                    "target_type": "blocking_condition",
                    "target_id": condition["condition_id"],
                    "source_wing": condition["wing_id"],
                    "event_type": "blocking_condition_event",
                    "required_fields": required_fields,
                    "required": True
                }
            )

    for gate in human_review_gates:
        if gate["trace_required"]:
            requirements.append(
                {
                    "requirement_id": f"trace.human_review_gate.{gate['gate_id']}",
                    "target_type": "human_review_gate",
                    "target_id": gate["gate_id"],
                    "source_wing": gate["source_wing"],
                    "event_type": "human_review_gate_event",
                    "required_fields": required_fields,
                    "required": True
                }
            )

    return requirements


def build_trace_coverage_matrix(
    trace_receipt_requirements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    coverage_matrix: List[Dict[str, Any]] = []

    for requirement in trace_receipt_requirements:
        coverage_matrix.append(
            {
                "coverage_id": f"coverage.{requirement['target_type']}.{requirement['target_id']}",
                "target_type": requirement["target_type"],
                "target_id": requirement["target_id"],
                "trace_requirement_id": requirement["requirement_id"],
                "covered": True
            }
        )

    return coverage_matrix


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
            "human_review_gates",
            "review_record_templates",
            "trace_receipt_requirements",
            "trace_coverage_matrix",
            "safety_boundary",
            "human_review",
            "trace_core"
        ],
        "properties": {
            "schema_version": {
                "type": "string",
                "const": "0.5.0"
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
            "human_review_gates": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/human_review_gate"
                }
            },
            "review_record_templates": {
                "$ref": "#/$defs/review_record_templates"
            },
            "trace_receipt_requirements": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/trace_receipt_requirement"
                }
            },
            "trace_coverage_matrix": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/trace_coverage_item"
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
            "event_type": {
                "type": "string",
                "enum": [
                    "wing_event",
                    "handoff_event",
                    "blocking_condition_event",
                    "human_review_gate_event"
                ]
            },
            "target_type": {
                "type": "string",
                "enum": [
                    "wing",
                    "handoff_rule",
                    "blocking_condition",
                    "human_review_gate"
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
                    "rule_id",
                    "from_wing",
                    "to_wing",
                    "condition"
                ],
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "minLength": 1
                    },
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
            "human_review_gate": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "gate_id",
                    "source_type",
                    "source_id",
                    "source_wing",
                    "severity",
                    "reviewer_role",
                    "review_trigger",
                    "escalation_target",
                    "approval_record_required",
                    "rejection_record_required",
                    "trace_required"
                ],
                "properties": {
                    "gate_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "source_type": {
                        "type": "string",
                        "enum": [
                            "wing",
                            "blocking_condition"
                        ]
                    },
                    "source_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "source_wing": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "severity": {
                        "$ref": "#/$defs/severity"
                    },
                    "reviewer_role": {
                        "type": "string",
                        "minLength": 1
                    },
                    "review_trigger": {
                        "type": "string",
                        "minLength": 1
                    },
                    "escalation_target": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "approval_record_required": {
                        "type": "boolean"
                    },
                    "rejection_record_required": {
                        "type": "boolean"
                    },
                    "trace_required": {
                        "type": "boolean"
                    }
                }
            },
            "review_record_templates": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "approval_record",
                    "rejection_record"
                ],
                "properties": {
                    "approval_record": {
                        "$ref": "#/$defs/review_record_template"
                    },
                    "rejection_record": {
                        "$ref": "#/$defs/review_record_template"
                    }
                }
            },
            "review_record_template": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "required_fields"
                ],
                "properties": {
                    "required_fields": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    }
                }
            },
            "trace_receipt_requirement": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "requirement_id",
                    "target_type",
                    "target_id",
                    "source_wing",
                    "event_type",
                    "required_fields",
                    "required"
                ],
                "properties": {
                    "requirement_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "target_type": {
                        "$ref": "#/$defs/target_type"
                    },
                    "target_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "source_wing": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "event_type": {
                        "$ref": "#/$defs/event_type"
                    },
                    "required_fields": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "required": {
                        "type": "boolean"
                    }
                }
            },
            "trace_coverage_item": {
                "type": "object",
                "additionalProperties": not strict,
                "required": [
                    "coverage_id",
                    "target_type",
                    "target_id",
                    "trace_requirement_id",
                    "covered"
                ],
                "properties": {
                    "coverage_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "target_type": {
                        "$ref": "#/$defs/target_type"
                    },
                    "target_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "trace_requirement_id": {
                        "type": "string",
                        "minLength": 1
                    },
                    "covered": {
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
                    "required_event_types",
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
                    "required_event_types": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "$ref": "#/$defs/event_type"
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

    handoff_rules = expand_handoff_rules(wings)
    blocking_conditions = expand_blocking_conditions(wings)
    boundary_escalation_map = build_boundary_escalation_map(wings)
    human_review_gates = build_human_review_gates(
        wings,
        global_rules["human_review"]["reviewer_role"]
    )
    review_record_templates = build_review_record_templates(global_rules)

    trace_receipt_requirements = build_trace_receipt_requirements(
        wings=wings,
        handoff_rules=handoff_rules,
        blocking_conditions=blocking_conditions,
        human_review_gates=human_review_gates,
        required_fields=global_rules["trace_receipt"]["required_fields"]
    )

    trace_coverage_matrix = build_trace_coverage_matrix(
        trace_receipt_requirements
    )

    return {
        "schema_version": "0.5.0",
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
        "handoff_rules": handoff_rules,
        "blocking_conditions": blocking_conditions,
        "boundary_escalation_map": boundary_escalation_map,
        "human_review_gates": human_review_gates,
        "review_record_templates": review_record_templates,
        "trace_receipt_requirements": trace_receipt_requirements,
        "trace_coverage_matrix": trace_coverage_matrix,
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
            "required_event_types": global_rules["trace_receipt"]["required_event_types"],
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
