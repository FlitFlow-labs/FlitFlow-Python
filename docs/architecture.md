# Python Runtime Architecture

Overview of the inner workings, components, and execution pipeline of the `flitflow` Python runtime (v1.0.0).

## Package Structure

```text
src/flitflow/
├── base.py         # BaseFunction, RuntimeResult, Status, Signal
├── engine.py       # RuntimeEngine (component traversal & state)
├── schema.py       # JSON Schema validation
└── functions/      # Built-in function handlers (control, array)

```

## Core Objects & Classes

### 1. `RuntimeEngine`

* Stores the AST and manages runtime `state`.
* Allows dynamic function registration via `register_function(name, func_instance)`.
* Triggers execution starting from the `"main"` component via `run(state)`.

### 2. `BaseFunction`

Base class for all executable handlers conforming to the unified execution pipeline:

1. **`run()`**: Pipeline wrapper that pre-evaluates `args`, delegates raw `params`, executes core logic, and automatically binds output to `target_variable`.
2. **`execute()`**: Abstract method containing the specific function logic.

### 3. `RuntimeResult`

Encapsulates execution status, return values, and control flow signals:

* **`status`**: `SUCCESS`, `WARNING`, or `ERROR`
* **`signal`**: `NONE`, `RETURN`, `BREAK`, or `CONTINUE`
* **`value`**: Return payload
* **`logs`**: Log messages and runtime warnings

## "Always Safe" Guarantee

Missing functions or out-of-bounds operations never throw unhandled Python exceptions. Instead, the runtime logs the issue, sets `RuntimeResult.status = Status.ERROR`, binds `None` to target variables, and continues execution safely.
