# src/flitflow/functions/control.py
from typing import Any
from flitflow.base import BaseFunction, RuntimeResult, Signal, Status


class SetVariablesFunction(BaseFunction):
    """`set_variables`: Set variables."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        if not isinstance(args, dict):
            return RuntimeResult(
                status=Status.WARNING,
                value=None,
                logs=["set_variables args must be a dict"],
            )

        last_val = None
        for key, val in args.items():
            state[key] = val
            last_val = val

        # When setting a single variable, return its value to support automatic binding to target_variable
        return_value = last_val if len(args) == 1 else args
        return RuntimeResult(status=Status.SUCCESS, value=return_value)


class SetGlobalVariablesFunction(BaseFunction):
    """`set_global_variables`: Set variables in the root execution state."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        if not isinstance(args, dict):
            return RuntimeResult(
                status=Status.WARNING,
                value=None,
                logs=["set_global_variables args must be a dict"],
            )

        last_val = None
        for key, val in args.items():
            # Change the root state directly to ensure global visibility across components
            engine.root_state[key] = val
            # state[key] = val  # Also update the current state to reflect the change
            state[key] = val
            last_val = val

        return_value = last_val if len(args) == 1 else args
        return RuntimeResult(status=Status.SUCCESS, value=return_value)


class CallComponentFunction(BaseFunction):
    """`call_component`: Invoke a subroutine."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        comp_name = args.get("name")
        if not comp_name or comp_name not in engine.ast:
            return RuntimeResult(
                status=Status.ERROR,
                value=None,
                logs=[f"Component '{comp_name}' not found."],
            )

        res = engine.execute_component(comp_name, state)

        # Consume the RETURN signal from a subroutine because it is meant to bubble back to the caller
        signal = res.signal
        if signal == Signal.RETURN or signal == "RETURN":
            signal = Signal.NONE

        return RuntimeResult(
            status=res.status,
            signal=signal,
            value=res.value,
            logs=res.logs,
        )


class SwitchFunction(BaseFunction):
    """`switch`: Conditional branching."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        raw_val = args.get("value")
        if isinstance(raw_val, bool):
            # Spec v1.1: bool MUST be normalized to lowercase strings
            val = str(raw_val).lower()
        else:
            val = str(raw_val)

        if not isinstance(params, dict):
            return RuntimeResult(
                status=Status.ERROR, logs=["switch 'params' must be a dict/object."]
            )

        # Resolve branch:
        # 1) exact case match
        # 2) default branch
        # 3) no-op normal completion + warning log
        if val in params:
            target_steps = params[val]
            return engine.execute_steps(target_steps, state.copy())

        if "default" in params:
            target_steps = params["default"]
            return engine.execute_steps(target_steps, state.copy())

        return RuntimeResult(
            status=Status.WARNING,
            value=None,
            logs=[f"switch unresolved branch: value={val}, no default provided."],
        )


class ForeachFunction(BaseFunction):
    """`foreach`: Loop processing."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        items = args.get("items", [])
        as_var = args.get("as", "item")
        index_var = args.get("index", "index")

        if not isinstance(items, list):
            # Safe guarantee: if the target is not a list, treat it as NULL and end safely
            return RuntimeResult(
                status=Status.WARNING,
                logs=[f"foreach target '{items}' is not a list."],
            )

        if not isinstance(params, list):
            return RuntimeResult(
                status=Status.ERROR, logs=["foreach 'params' must be a list of steps."]
            )

        overall_res = RuntimeResult()
        engine.loop_depth += 1  # Increment loop depth for signal handling

        for idx, item in enumerate(items):
            # Spec v1.1: nested-step execution uses shallow-copied child state
            child_state = state.copy()
            child_state[as_var] = item
            child_state[index_var] = idx

            # in_loop=True: to bubble BREAK/CONTINUE signals to the loop boundary
            res = engine.execute_steps(params, child_state)
            overall_res.merge(res)
            overall_res.value = res.value

            # Handle BREAK / CONTINUE / RETURN signals
            if res.signal == Signal.BREAK:
                break
            elif res.signal == Signal.CONTINUE:
                # Continue is consumed at loop boundary
                continue
            elif res.signal == Signal.RETURN:
                overall_res.signal = Signal.RETURN
                break
        engine.loop_depth -= 1  # Decrement loop depth after loop completion
        return overall_res


class BreakFunction(BaseFunction):
    """`break`: Interrupt a loop."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        return RuntimeResult(signal=Signal.BREAK)


class ContinueFunction(BaseFunction):
    """`continue`: Skip the current loop iteration."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        return RuntimeResult(signal=Signal.CONTINUE)


class ReturnFunction(BaseFunction):
    """`return`: Exit a component."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        ret_val = args.get("value")
        return RuntimeResult(signal=Signal.RETURN, value=ret_val)
