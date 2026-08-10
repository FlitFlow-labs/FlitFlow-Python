# Getting Started with `flitflow`

`flitflow` (v1.0.0) is a lightweight, safe, and portable Python runtime engine designed to execute FlitFlow DSL scripts defined as JSON/YAML ASTs.

## Installation

Install locally in editable mode:

```bash
pip install -e .[dev]

```

Or install via PyPI:

```bash
pip install flitflow

```

---

## Basic Usage

Here is a simple example to get up and running:

```python
from flitflow import RuntimeEngine, register_builtin_functions, validate_ast

# 1. Define an AST script matching FlitFlow Core Spec v1.0
ast = {
    "main": [
        {
            "function": "set_variables",
            "args": {"message": "Hello, FlitFlow!"}
        }
    ]
}

# 2. Validate against schema
is_valid, error = validate_ast(ast)
if not is_valid:
    raise ValueError(f"Invalid AST: {error}")

# 3. Initialize engine & register standard functions
engine = RuntimeEngine(ast)
register_builtin_functions(engine)

# 4. Execute
state = {}
result = engine.run(state)

print(state.get("message"))  # Output: Hello, FlitFlow!
print(result.status)         # Output: Status.SUCCESS

```
