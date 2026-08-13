# Logging Policy (FlitFlow-Python)

## 1. Baseline

Logging behavior follows the Python runtime reference baseline for FlitFlow.

Minimum abnormal events that emit logs:

1. undefined function invocation
2. missing component target
3. invalid type operation
4. out-of-bounds access
5. out-of-context control signal (`break` / `continue` outside loop)
6. unresolved `switch` branch (no match and no `default`)

## 2. Compatibility

Custom log fields are allowed, but extensions must remain backward-compatible with baseline consumers that parse existing message-oriented logs.

## 3. Message Stability Guidance

- Keep existing message meaning stable across patch versions.
- If changing message wording, preserve semantic intent and severity classification.

## 4. Suggested Structured Extension (Optional)

Example optional metadata fields:

- `code`
- `severity`
- `function`
- `context`
- `timestamp`
