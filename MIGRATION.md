# Migration Guide (v1.0 -> v1.1)

This guide explains how to migrate FlitFlow-Python runtime behavior to v1.1-aligned semantics.

## 1. Runtime Behavior Changes

### 1.1 `switch` boolean normalization

`switch` comparison values now normalize booleans to lowercase strings:

- `True` -> `"true"`
- `False` -> `"false"`

If your branch keys used `"True"`/`"False"`, update them to lowercase.

### 1.2 `switch` with no match and no `default`

When no case matches and no `default` exists:

- runtime completes normally (no crash),
- no child steps are executed (no-op),
- warning log is emitted for unresolved branch.

### 1.3 Nested step scope

Nested blocks (e.g., `foreach` body, selected `switch` branch) execute using shallow-copied child state.

This can affect scripts that relied on implicit mutation of parent scope from nested execution.

### 1.4 Out-of-loop `break` / `continue`

If `break` or `continue` appears outside loop context:

- warning is logged,
- signal is ignored,
- execution continues.

## 2. Recommended Upgrade Procedure

1. Update to runtime version `1.1.0`.
2. Re-run conformance tests (`pytest -v`).
3. Review switch branch keys for bool cases (`"true"`, `"false"`).
4. Validate scripts that depended on nested implicit parent-state mutation.
5. Review logs/monitoring filters for new warning messages.

## 3. Risk Checklist

- [ ] bool switch keys are lowercase
- [ ] no-default switch paths are acceptable as no-op
- [ ] nested state assumptions validated
- [ ] operational alert rules updated for warning logs
