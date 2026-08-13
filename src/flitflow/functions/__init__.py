from flitflow.engine import RuntimeEngine
from flitflow.functions.control import (
    SetVariablesFunction,
    SetGlobalVariablesFunction,
    CallComponentFunction,
    SwitchFunction,
    ForeachFunction,
    BreakFunction,
    ContinueFunction,
    ReturnFunction,
)
from flitflow.functions.array import (
    ArrayCreateFunction,
    ArrayPushFunction,
    ArrayGetFunction,
    ArrayLengthFunction,
)


def register_builtin_functions(engine: RuntimeEngine) -> None:
    """Register all built-in functions with the engine."""
    builtins = {
        # Control Flow
        "set_variables": SetVariablesFunction(),
        "set_global_variables": SetGlobalVariablesFunction(),
        "call_component": CallComponentFunction(),
        "switch": SwitchFunction(),
        "foreach": ForeachFunction(),
        "break": BreakFunction(),
        "continue": ContinueFunction(),
        "return": ReturnFunction(),
        # Array Operations
        "array_create": ArrayCreateFunction(),
        "array_push": ArrayPushFunction(),
        "array_get": ArrayGetFunction(),
        "array_length": ArrayLengthFunction(),
    }

    for name, func_impl in builtins.items():
        engine.register_function(name, func_impl)
