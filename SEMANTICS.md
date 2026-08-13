# Execution Semantics (FlitFlow-Python)

This document summarizes operational semantics used by the Python runtime.

## 1. Step Pipeline

For each step:

1. resolve function by `function` key
2. pre-evaluate `args`
3. pass `params` raw/deferred
4. invoke function handler
5. bind `target_variable` when `signal == NONE`
6. merge logs/status/value
7. propagate/consume control signal by boundary rules

## 2. State Model

- Top-level execution uses active state map.
- Nested step arrays execute on shallow-copied child state.
- This prevents implicit leakage of loop-local variables to outer scope.

## 3. Signal Boundaries

- `BREAK` / `CONTINUE` are consumed at loop boundary.
- `RETURN` terminates current component frame.
- `call_component` consumes callee `RETURN` so caller can continue.

## 4. Switch Resolution

- Compare on string-normalized value.
- Booleans normalize to lowercase strings (`"true"`, `"false"`).
- Fallback order:
  1. matching case
  2. `default`
  3. no-op completion + warning log

## 5. Safety Invariant

No uncaught exceptions should terminate script execution.
All abnormal outcomes are represented in `RuntimeResult`.
