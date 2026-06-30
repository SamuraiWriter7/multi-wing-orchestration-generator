#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object at root: {path}")
    return data


def build_generated_schema(definition: Dict[str, Any]) -> Dict[str, Any]:
    target = definition["target"]
    wings = definition["wings"]
    global_rules = definition["global_rules"]
    strict = definition["generator_config"]["strict_additional_properties"]

    wing_ids = [wing["wing_id"] for wing in wings]

    schema: Dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": target["output_schema_id"],
        "title": target["output_schema_title"],
        "description": "Generated Multi-Wing Defensive Orchestration schema.",
        "type": "object",
        "additionalProperties": strict is False,
        "required": [
            "schema_version",
            "orchestration_id",
            "created_at",
            "wings",
            "handoff_rules",
            "blocking_conditions",
            "safety_boundary",
            "human_review",
            "trace_core"
        ],
        "properties": {
            "schema_version": {
                "type": "string",
                "const": "0.1.0"
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
            "wing_state": {
                "type": "object",
                "additionalProperties": strict is False,
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
                        "items": {
                            "type": "string"
                        }
                    },
                    "prohibited_outputs": {
                        "type": "array",
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
                "additionalProperties": strict is False,
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
                "additionalProperties": strict is False,
                "required": [
                    "wing_id",
                    "condition",
                    "severity"
                ],
                "properties": {
                    "wing_id": {
                        "$ref": "#/$defs/wing_id"
                    },
                    "condition": {
                        "type": "string",
                        "minLength": 1
                    },
                    "severity": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical"
                        ]
                    }
                }
            },
            "safety_boundary": {
                "type": "object",
                "additionalProperties": strict is False,
                "required": [
                    "prohibited_uses",
                    "escalation_conditions"
                ],
                "properties": {
                    "prohibited_uses": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "default": global_rules["safety_boundary"]["prohibited_uses"]
                    },
                    "escalation_conditions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "default": global_rules["safety_boundary"]["escalation_conditions"]
                    }
                }
            },
            "human_review": {
                "type": "object",
                "additionalProperties": strict is False,
                "required": [
                    "required",
                    "reviewer_role",
                    "review_triggers"
                ],
                "properties": {
                    "required": {
                        "type": "boolean",
                        "default": global_rules["human_review"]["required"]
                    },
                    "reviewer_role": {
                        "type": "string",
                        "default": global_rules["human_review"]["reviewer_role"]
                    },
                    "review_triggers": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "default": global_rules["human_review"]["review_triggers"]
                    }
                }
            },
            "trace_core": {
                "type": "object",
                "additionalProperties": strict is False,
                "required": [
                    "enabled",
                    "required_trace_fields",
                    "required_orchestration_fields"
                ],
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": global_rules["trace_receipt"]["enabled"]
                    },
                    "required_trace_fields": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "default": global_rules["trace_receipt"]["required_fields"]
                    },
                    "required_orchestration_fields": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "default": global_rules["orchestration_receipt"]["required_fields"]
                    }
                }
            }
        }
    }

    return schema


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Multi-Wing Orchestration JSON Schema from a wing definition YAML."
    )
    parser.add_argument(
        "definition",
        type=Path,
        help="Path to wing-definition YAML."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for generated JSON Schema."
    )
    args = parser.parse_args()

    definition = load_yaml(args.definition)
    generated_schema = build_generated_schema(definition)

    output_directory = Path(definition["generator_config"]["output_directory"])
    output_filename = definition["target"]["output_schema_filename"]
    output_path = args.output or output_directory / output_filename

    write_json(output_path, generated_schema)
    print(f"[generated] {output_path}")


if __name__ == "__main__":
    main()
