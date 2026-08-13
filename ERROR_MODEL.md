# Error Model (FlitFlow-Python)

## 1. Status Levels

Runtime uses:

- `SUCCESS`
- `WARNING`
- `ERROR`

## 2. Classification Policy

Default rule:

- Abnormal but recoverable conditions -> `WARNING`

Escalation rule:

- Fatal conditions for correct continuation of the current context -> `ERROR`

Always Safe rule:

- Even `ERROR` MUST remain non-crashing and represented via `RuntimeResult`.

## 3. Typical Classification Examples

### WARNING (default abnormal)

- invalid type in array operations
- out-of-bounds array access handled safely (`NULL` return)
- unresolved `switch` branch with no `default`
- out-of-loop `break` / `continue` (ignored after warning)

### ERROR (fatal to correct continuation context)

- undefined function invocation in active pipeline
- missing required component on explicit `call_component`

## 4. Aggregation Priority

Merged status priority:

`ERROR > WARNING > SUCCESS`
