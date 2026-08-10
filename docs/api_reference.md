# API Reference

Public classes and utility functions exported by `flitflow` (v1.0.0).

## Classes

### `RuntimeEngine(ast: dict[str, Any])`

Main execution engine for FlitFlow scripts.

- **`run(state: dict[str, Any] | None = None) -> RuntimeResult`**: Executes from entry point `"main"`.
- **`register_function(name: str, func: BaseFunction)`**: Registers a custom function handler.
- **`execute_component(name: str, state: dict[str, Any]) -> RuntimeResult`**: Executes a specific named subroutine.

---

### `BaseFunction`

Abstract base class for function implementations.

- **`execute(args, params, state, engine) -> RuntimeResult`**: [Abstract] Core execution logic handler.

---

### `RuntimeResult`

Unified execution result container.

- **Attributes**:
  - `status` (`Status`): Status enum (`SUCCESS`, `WARNING`, `ERROR`).
  - `signal` (`Signal`): Signal enum (`NONE`, `RETURN`, `BREAK`, `CONTINUE`).
  - `value` (`Any`): Return payload.
  - `logs` (`list[str]`): Log messages.

---

## Functions

### `validate_ast(ast: dict[str, Any]) -> tuple[bool, str | None]`

Validates AST structure against `core_schema.json`.

### `register_builtin_functions(engine: RuntimeEngine)`

Registers all standard built-in functions (`foreach`, `switch`, `set_variables`, array helpers, etc.).
