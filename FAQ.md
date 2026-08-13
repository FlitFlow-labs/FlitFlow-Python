# FAQ (FlitFlow-Python)

## Q1. Does FlitFlow guarantee compatibility with other DSL runtimes?

No. FlitFlow is an independent DSL.  
Normative behavior is defined by FlitFlow Core Spec + this runtime's conformance behavior.

## Q2. What does `NULL` mean in Python runtime?

`NULL` maps to Python `None`.

## Q3. What happens when `switch` has no matching case and no `default`?

Execution completes normally as a no-op branch, and a warning log is emitted.

## Q4. Are boolean switch branches case-sensitive?

Boolean values are normalized to lowercase string keys:

- `"true"`
- `"false"`

## Q5. Can `break` / `continue` crash runtime outside loops?

No. They are logged as warnings, ignored as control signals, and execution continues.

## Q6. Does `target_variable` overwrite existing values?

Yes, when binding is applicable (`signal == NONE`), overwrite is by default.

## Q7. Why did some previous scripts change behavior after v1.1 alignment?

Likely due to clarified semantics:

- bool switch normalization
- no-default switch warning/no-op
- nested shallow-copy scope rules
- out-of-loop signal handling
