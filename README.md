# FlitFlow (`flitflow`)

[![PyPI version](https://badge.fury.io/py/flitflow.svg)](https://badge.fury.io/py/flitflow)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/flitflow.svg)](https://pypi.org/project/flitflow/)

A lightweight, safe, and portable Python runtime engine for executing FlitFlow DSL scripts defined as structured JSON/YAML ASTs.

---

## Key Features

- **"Always Safe" Execution**: Never crashes on missing functions or runtime evaluation errors. It safely logs warnings/errors to `RuntimeResult` and continues execution.
- **Unified Pipeline (`BaseFunction`)**: Pre-evaluates function arguments (`args`), safely delegates deferred parameter blocks (`params`), and automatically binds results to `target_variable`.
- **Control Signal Bubbling**: Native handling of control flow signals (`RETURN`, `BREAK`, `CONTINUE`) across execution stacks.
- **AST Schema Validation**: Built-in JSON Schema validator (`validate_ast`) ensuring script structural conformance before runtime execution.

---

## Installation

```bash
pip install flitflow

```

Or install locally for development:

```bash
pip install -e .[dev]

```

---

## Quick Start

```python
from flitflow import RuntimeEngine, register_builtin_functions, validate_ast

# 1. Define AST script
ast = {
    "main": [
        {
            "function": "set_variables",
            "args": {"name": "FlitFlow", "items": ["Python", "DSL"]}
        },
        {
            "function": "array_create",
            "target_variable": "my_list"
        },
        {
            "function": "foreach",
            "args": {"items": "items", "as": "item"},
            "params": [
                {
                    "function": "array_push",
                    "args": {"array": "my_list", "value": "item"}
                }
            ]
        }
    ]
}

# 2. Validate AST structure
is_valid, error = validate_ast(ast)
if not is_valid:
    raise ValueError(f"Schema Validation Error: {error}")

# 3. Initialize engine & register built-in functions
engine = RuntimeEngine(ast)
register_builtin_functions(engine)

# 4. Execute
state = {}
result = engine.run(state)

print("Final State:", state)
# Output: {'name': 'FlitFlow', 'items': ['Python', 'DSL'], 'my_list': ['Python', 'DSL']}

print("Execution Status:", result.status)  # Status.SUCCESS

```

---

## Custom Functions

Extending `flitflow` is as simple as subclassing `BaseFunction`:

```python
from typing import Any
from flitflow import BaseFunction, RuntimeResult, Status

class CustomHelloFunction(BaseFunction):
    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        name = args.get("name", "World")
        return RuntimeResult(status=Status.SUCCESS, value=f"Hello, {name}!")

# Register to engine
engine.register_function("custom_hello", CustomHelloFunction())

```

---

## Documentation

For more detailed guides and API specifications, check out the [`docs/`](./docs) directory:

- [Getting Started](./docs/getting_started.md)
- [Python Runtime Architecture](./docs/architecture.md)
- [Writing Custom Functions](./docs/custom_functions.md)
- [API Reference](./docs/api_reference.md)

---

## Testing

Run conformance and unit tests using `pytest`:

```bash
pytest -v

```

---

## License

This project is licensed under the [MIT License](./LICENSE).
