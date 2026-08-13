from typing import Any, Optional
from flitflow.base import BaseFunction, RuntimeResult, Signal, Status
from flitflow.schema import validate_ast


class RuntimeEngine:
    """Core implementation of the FlitFlow execution engine."""

    def __init__(self, ast: dict[str, Any]):
        self.ast = ast
        self.functions: dict[str, BaseFunction] = {}
        self.root_state: dict[str, Any] = {}
        self.loop_depth = 0  # Track the current loop depth for signal handling

    def register_function(self, name: str, func_impl: BaseFunction) -> None:
        """Register built-in or custom functions."""
        self.functions[name] = func_impl

    def evaluate_value(self, val: Any, state: dict[str, Any]) -> Any:
        """Evaluate variable references (return the value from state if the key exists, otherwise treat it as a literal)."""
        if isinstance(val, str) and val in state:
            return state[val]
        return val

    def evaluate_args(
        self, raw_args: dict[str, Any], state: dict[str, Any]
    ) -> dict[str, Any]:
        """Pre-evaluate variable references inside args."""
        evaluated = {}
        for key, val in raw_args.items():
            evaluated[key] = self.evaluate_value(val, state)
        return evaluated

    def execute_steps(
        self,
        steps: list[dict[str, Any]],
        state: dict[str, Any],
    ) -> RuntimeResult:
        """Sequential execution loop for the step array."""
        overall_result = RuntimeResult()

        for step in steps:
            func_name = step.get("function")
            raw_args = step.get("args", {})
            params = step.get("params")
            target_var = step.get("target_variable")

            # 1. Function Resolution
            if not isinstance(func_name, str):
                overall_result.logs.append(
                    f"Undefined function invocation: '{func_name}'"
                )
                overall_result.status = Status.ERROR
                if target_var:
                    state[target_var] = None
                continue

            func = self.functions.get(func_name)
            if not func:
                # SPEC 1.1.1: Record an error log, bind NULL safely, and continue
                overall_result.logs.append(
                    f"Undefined function invocation: '{func_name}'"
                )
                overall_result.status = Status.ERROR
                if target_var:
                    state[target_var] = None
                continue

            # 2. Pipeline Execution (call BaseFunction.run)
            step_result = func.run(
                raw_args=raw_args,
                params=params,
                target_variable=target_var,
                state=state,
                engine=self,
            )

            # Merge logs and status
            overall_result.merge(step_result)
            overall_result.value = step_result.value

            if step_result.signal != Signal.NONE:
                if step_result.signal in (Signal.BREAK, Signal.CONTINUE):
                    if self.loop_depth > 0:
                        # in-loop: propagate the signal to the loop boundary
                        overall_result.signal = step_result.signal
                        break
                    else:
                        # out-of-loop: log a warning and continue execution (do not propagate the signal)
                        overall_result.logs.append(
                            f"Out-of-loop control signal ignored: {step_result.signal}"
                        )
                        if overall_result.status == Status.SUCCESS:
                            overall_result.status = Status.WARNING
                        
                        # not setting signal to NONE here, so that the next steps can continue normally
                        continue

                # RETURN signal must always propagate to the caller, regardless of loop depth
                overall_result.signal = step_result.signal
                break

        return overall_result

    def execute_component(
        self, component_name: str, state: dict[str, Any]
    ) -> RuntimeResult:
        """Execute a component (subroutine)."""
        steps = self.ast.get(component_name)
        if steps is None:
            res = RuntimeResult(status=Status.ERROR)
            res.logs.append(f"Component not found: '{component_name}'")
            return res

        return self.execute_steps(steps, state)

    def run(self, initial_state: Optional[dict[str, Any]] = None) -> RuntimeResult:
        """Main entry point (execute the 'main' component)."""
        # Schema validation
        is_valid, err_msg = validate_ast(self.ast)
        if not is_valid:
            return RuntimeResult(
                status=Status.ERROR,
                logs=[f"AST Schema Validation Error: {err_msg}"],
            )
        self.root_state = initial_state if initial_state is not None else {}
        res = self.execute_component("main", self.root_state)
        if res.signal in (Signal.BREAK, Signal.CONTINUE):
            res.logs.append(f"Out-of-loop control signal ignored: {res.signal}")
            if res.status == Status.SUCCESS:
                res.status = Status.WARNING
            res.signal = Signal.NONE
        return res
        