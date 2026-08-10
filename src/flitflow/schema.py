from typing import Any, Tuple, Optional
import jsonschema

# Definition of core_schema.json
CORE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["main"],
    "additionalProperties": {
        "type": "array",
        "items": {"$ref": "#/$defs/Step"},
    },
    "$defs": {
        "Step": {
            "type": "object",
            "required": ["function"],
            "properties": {
                "function": {"type": "string"},
                "args": {"type": "object", "additionalProperties": True},
                "params": {
                    "oneOf": [
                        {
                            "type": "array",
                            "items": {"$ref": "#/$defs/Step"},
                        },
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/Step"},
                            },
                        },
                    ]
                },
                "target_variable": {"type": "string"},
            },
            "additionalProperties": False,
        }
    },
}


def validate_ast(ast: dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate whether the AST conforms to the FlitFlow specification."""
    try:
        jsonschema.validate(instance=ast, schema=CORE_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message
