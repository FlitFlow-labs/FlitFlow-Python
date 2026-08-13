# Conformance Matrix (FlitFlow-Python)

This matrix maps FlitFlow Core Spec requirements to this runtime's conformance tests.

| Requirement ID | Summary | Test Reference |
| --- | --- | --- |
| FF-RT-001 | Always Safe (no runtime crash) | `test_tc_safe_01_undefined_function`, `test_tc_safe_02_out_of_bounds_and_invalid_types`, `test_tc_ctrl_06_out_of_loop_break_continue` |
| FF-RT-002 | Undefined function logs + safe continuation | `test_tc_safe_01_undefined_function` |
| FF-RT-003 | `target_variable` binds only when `signal == NONE` | `test_tc_pipe_03_automatic_variable_binding`, `test_tc_ctrl_07_return_signal_bubbling` |
| FF-RT-004 | `target_variable` overwrite behavior | `test_tc_pipe_04_target_variable_overwrite` |
| FF-RT-005 | `switch` match/default fallback | `test_tc_ctrl_01_switch_branching` |
| FF-RT-006 | `switch` bool lowercase normalization | `test_tc_ctrl_02_switch_bool_lowercase_normalization` |
| FF-RT-007 | `switch` no match/no default => no-op + warning | `test_tc_ctrl_03_switch_no_match_no_default_warning` |
| FF-RT-008 | `CONTINUE` loop boundary behavior | `test_tc_ctrl_05_break_and_continue` |
| FF-RT-009 | `BREAK` loop boundary behavior | `test_tc_ctrl_05_break_and_continue` |
| FF-RT-010 | Out-of-loop break/continue warning+ignore | `test_tc_ctrl_06_out_of_loop_break_continue` |
| FF-RT-011 | `RETURN` consumed at `call_component` boundary | `test_tc_ctrl_07_return_signal_bubbling` |
| FF-RT-012 | Nested execution shallow-copy scope | `test_tc_scope_01_nested_step_shallow_copy` |
| FF-RT-013 | Schema failure aborts safely | existing schema validation execution-path tests |
| FF-RT-014 | Baseline logging compatibility | log assertions across safety/control tests |
| FF-RT-015 | Logging extensibility backward-compatibility | implementation policy + compatibility checks |

## Notes

- This matrix is intended for CI traceability and release readiness checks.
- Keep entries synchronized when adding/renaming tests.
