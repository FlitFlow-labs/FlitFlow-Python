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
        val = str(args.get("value"))
        if not isinstance(params, dict):
            return RuntimeResult(
                status=Status.ERROR, logs=["switch 'params' must be a dict/object."]
            )

        # Select the matching case, or use the default case if none matches
        target_steps = params.get(val, params.get("default", []))
        return engine.execute_steps(target_steps, state)


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

        for idx, item in enumerate(items):
            state[as_var] = item
            state[index_var] = idx

            res = engine.execute_steps(params, state)
            overall_res.merge(res)
            overall_res.value = res.value

            # Handle BREAK / CONTINUE signals
            if res.signal == Signal.BREAK:
                break
            elif res.signal == Signal.RETURN:
                overall_res.signal = Signal.RETURN
                break
            # For CONTINUE, proceed to the next loop iteration

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
