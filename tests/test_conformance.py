from flitflow.schema import validate_ast
from flitflow.base import Status


# ==========================================
# 1. Schema Validation Suite (TC-SCHEMA)
# ==========================================

def test_tc_schema_01_valid_minimal():
    """TC-SCHEMA-01: Minimal valid script structure"""
    ast = {"main": [{"function": "set_variables", "args": {"v": 1}}]}
    is_valid, err = validate_ast(ast)
    assert is_valid is True
    assert err is None


def test_tc_schema_02_missing_main():
    """TC-SCHEMA-02: Missing main entry point"""
    ast = {"sub_flow": [{"function": "set_variables", "args": {"v": 1}}]}
    is_valid, err = validate_ast(ast)
    assert is_valid is False
    assert err is not None


def test_tc_schema_03_params_structure():
    """TC-SCHEMA-03: Accept both arrays and objects in params"""
    ast = {
        "main": [
            {
                "function": "foreach",
                "params": [{"function": "set_variables", "args": {"x": 1}}],
            },
            {
                "function": "switch",
                "params": {
                    "case_a": [{"function": "set_variables", "args": {"x": 2}}]
                },
            },
        ]
    }
    is_valid, err = validate_ast(ast)
    assert is_valid is True


def test_tc_schema_04_invalid_properties():
    """TC-SCHEMA-04: Detect undefined keys inside a step"""
    ast = {"main": [{"function": "set_variables", "invalid_key": "fail"}]}
    is_valid, err = validate_ast(ast)
    assert is_valid is False


# ==========================================
# 2. Pipeline & Lifecycle Suite (TC-PIPE)
# ==========================================

def test_tc_pipe_01_arg_pre_evaluation(create_engine):
    """TC-PIPE-01: Pre-evaluate arguments in args"""
    ast = {
        "main": [
            {
                "function": "set_variables",
                "args": {"result": "base_val"},
                "target_variable": "evaluated_val",
            }
        ]
    }
    engine = create_engine(ast)
    state = {"base_val": 10}
    engine.run(state)
    assert state.get("evaluated_val") == 10


def test_tc_pipe_02_deferred_block_injection(create_engine):
    """TC-PIPE-02: Inject deferred blocks via params"""
    ast = {
        "main": [
            {
                "function": "foreach",
                "args": {"items": [1, 2]},
                "params": [
                    {"function": "set_variables", "args": {"counter": "item"}}
                ],
            }
        ]
    }
    engine = create_engine(ast)
    state = {}
    engine.run(state)
    assert state.get("counter") == 2


def test_tc_pipe_03_automatic_variable_binding(create_engine):
    """TC-PIPE-03: Automatically bind to a variable via target_variable"""
    ast = {"main": [{"function": "array_create", "target_variable": "my_list"}]}
    engine = create_engine(ast)
    state = {}
    engine.run(state)
    assert state.get("my_list") == []


# ==========================================
# 3. Always Safe Guarantee Suite (TC-SAFE)
# ==========================================

def test_tc_safe_01_undefined_function(create_engine):
    """TC-SAFE-01: Continue safely without crashing when an undefined function is invoked"""
    ast = {
        "main": [
            {"function": "unknown_nonexistent_func", "target_variable": "res"},
            {"function": "set_variables", "args": {"status": "ok"}},
        ]
    }
    engine = create_engine(ast)
    state = {}
    res = engine.run(state)

    assert state.get("res") is None
    assert state.get("status") == "ok"
    assert res.status == Status.ERROR
    assert len(res.logs) > 0


def test_tc_safe_02_out_of_bounds_and_invalid_types(create_engine):
    """TC-SAFE-02: Handle out-of-bounds access and invalid types safely"""
    ast = {
        "main": [
            {
                "function": "array_get",
                "args": {"array": "not_an_array", "index": 99},
                "target_variable": "val1",
            },
            {
                "function": "array_get",
                "args": {"array": [], "index": 5},
                "target_variable": "val2",
            },
        ]
    }
    engine = create_engine(ast)
    state = {}
    engine.run(state)

    assert state.get("val1") is None
    assert state.get("val2") is None


# ==========================================
# 4. Control Flow & Signals Suite (TC-CTRL)
# ==========================================

def test_tc_ctrl_01_switch_branching(create_engine):
    """TC-CTRL-01: switch branching and default fallback"""
    ast = {
        "main": [
            {
                "function": "switch",
                "args": {"value": "role"},
                "params": {
                    "admin": [
                        {
                            "function": "set_variables",
                            "args": {"permission": "all"},
                        }
                    ],
                    "default": [
                        {
                            "function": "set_variables",
                            "args": {"permission": "read"},
                        }
                    ],
                },
            }
        ]
    }

    # Matching case (admin)
    engine1 = create_engine(ast)
    state1 = {"role": "admin"}
    engine1.run(state1)
    assert state1.get("permission") == "all"

    # Default case (unknown)
    engine2 = create_engine(ast)
    state2 = {"role": "unknown"}
    engine2.run(state2)
    assert state2.get("permission") == "read"


def test_tc_ctrl_02_foreach_loop(create_engine):
    """TC-CTRL-02: foreach loop and scope variable updates"""
    ast = {
        "main": [
            {"function": "array_create", "target_variable": "output"},
            {
                "function": "foreach",
                "args": {"items": "list", "as": "item"},
                "params": [
                    {
                        "function": "array_push",
                        "args": {"array": "output", "value": "item"},
                    }
                ],
            },
        ]
    }
    engine = create_engine(ast)
    state = {"list": ["a", "b"]}
    engine.run(state)
    assert state.get("output") == ["a", "b"]


def test_tc_ctrl_03_break_and_continue(create_engine):
    """TC-CTRL-03: Control break and continue signals"""
    ast = {
        "main": [
            {"function": "array_create", "target_variable": "out"},
            {
                "function": "foreach",
                "args": {"items": "list", "as": "num"},
                "params": [
                    {
                        "function": "switch",
                        "args": {"value": "num"},
                        "params": {
                            "2": [{"function": "continue"}],
                            "4": [{"function": "break"}],
                        },
                    },
                    {
                        "function": "array_push",
                        "args": {"array": "out", "value": "num"},
                    },
                ],
            },
        ]
    }
    engine = create_engine(ast)
    state = {"list": [1, 2, 3, 4]}
    engine.run(state)
    assert state.get("out") == [1, 3]


def test_tc_ctrl_04_return_signal_bubbling(create_engine):
    """TC-CTRL-04: Propagate the return signal"""
    ast = {
        "main": [
            {"function": "call_component", "args": {"name": "sub"}},
            {"function": "set_variables", "args": {"after_call": True}},
        ],
        "sub": [
            {"function": "set_variables", "args": {"sub_started": True}},
            {"function": "return", "args": {"value": "stopped"}},
            {"function": "set_variables", "args": {"sub_finished": True}},
        ],
    }
    engine = create_engine(ast)
    state = {}
    engine.run(state)

    assert state.get("sub_started") is True
    assert "sub_finished" not in state
    assert state.get("after_call") is True


# ==========================================
# 5. Subroutine Suite (TC-COMP)
# ==========================================

def test_tc_comp_01_call_component(create_engine):
    """TC-COMP-01: Execute call_component and share state"""
    ast = {
        "main": [{"function": "call_component", "args": {"name": "init"}}],
        "init": [{"function": "set_variables", "args": {"initialized": True}}],
    }
    engine = create_engine(ast)
    state = {}
    engine.run(state)
    assert state.get("initialized") is True
