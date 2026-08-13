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
                    {
                        "function": "set_global_variables",
                        "args": {"counter": "item"},
                    }
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


def test_tc_pipe_04_target_variable_overwrite(create_engine):
    """TC-PIPE-04: target_variable overwrites existing value by default"""
    ast = {"main": [{"function": "array_create", "target_variable": "my_list"}]}
    engine = create_engine(ast)
    state = {"my_list": [1, 2, 3]}
    engine.run(state)
    assert state.get("my_list") == []


def test_tc_pipe_05_global_variable_assignment(create_engine):
    """TC-PIPE-05: set_global_variables assigns key-value pairs to root state"""
    ast = {
        "main": [
            {
                "function": "set_global_variables",
                "args": {"global_a": 100, "global_b": "hello"},
                "target_variable": "assign_res",
            }
        ]
    }
    engine = create_engine(ast)
    state = {}
    res = engine.run(state)

    assert state.get("global_a") == 100
    assert state.get("global_b") == "hello"
    assert res.value == {"global_a": 100, "global_b": "hello"}


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
    res = engine.run(state)

    assert state.get("val1") is None
    assert state.get("val2") is None
    assert res.status in (Status.WARNING, Status.ERROR)


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
                            "function": "set_global_variables",
                            "args": {"permission": "all"},
                        }
                    ],
                    "default": [
                        {
                            "function": "set_global_variables",
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


def test_tc_ctrl_02_switch_bool_lowercase_normalization(create_engine):
    """TC-CTRL-02: Bool switch keys normalize to lowercase strings."""
    ast = {
        "main": [
            {
                "function": "switch",
                "args": {"value": "is_express"},
                "params": {
                    "true": [
                        {
                            "function": "set_global_variables",
                            "args": {"label": "exp"},
                        }
                    ],
                    "false": [
                        {
                            "function": "set_global_variables",
                            "args": {"label": "local"},
                        }
                    ],
                },
            }
        ]
    }

    engine1 = create_engine(ast)
    state1 = {"is_express": True}
    engine1.run(state1)
    assert state1.get("label") == "exp"

    engine2 = create_engine(ast)
    state2 = {"is_express": False}
    engine2.run(state2)
    assert state2.get("label") == "local"


def test_tc_ctrl_03_switch_no_match_no_default_warning(create_engine):
    """TC-CTRL-03: no match + no default => normal completion with warning log."""
    ast = {
        "main": [
            {
                "function": "switch",
                "args": {"value": "role"},
                "params": {
                    "admin": [
                        {
                            "function": "set_global_variables",
                            "args": {"permission": "all"},
                        }
                    ]
                },
            },
            {"function": "set_variables", "args": {"after_switch": True}},
        ]
    }
    engine = create_engine(ast)
    state = {"role": "unknown"}
    res = engine.run(state)

    assert state.get("after_switch") is True
    assert res.status in (Status.WARNING, Status.ERROR)
    assert any("unresolved branch" in log for log in res.logs)


def test_tc_ctrl_04_foreach_loop(create_engine):
    """TC-CTRL-04: foreach loop basic execution"""
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
    # Shallow copy shares object references, so array_push mutates output
    assert state.get("output") == ["a", "b"]


def test_tc_ctrl_05_break_and_continue(create_engine):
    """TC-CTRL-05: Control break and continue signals in loop"""
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
    # Shallow copy shares object references, so out is mutated
    assert state.get("out") == [1, 3]


def test_tc_ctrl_06_out_of_loop_break_continue(create_engine):
    """TC-CTRL-06: Out-of-loop break/continue => warning + ignored + continue."""
    ast = {
        "main": [
            {"function": "break"},
            {"function": "continue"},
            {"function": "set_variables", "args": {"alive": True}},
        ]
    }
    engine = create_engine(ast)
    state = {}
    res = engine.run(state)

    assert state.get("alive") is True
    assert res.status in (Status.WARNING, Status.ERROR)
    assert any("Out-of-loop control signal ignored" in log for log in res.logs)


def test_tc_ctrl_07_return_signal_bubbling(create_engine):
    """TC-CTRL-07: Propagate the return signal boundary via call_component"""
    ast = {
        "main": [
            {"function": "call_component", "args": {"name": "sub"}},
            {"function": "set_variables", "args": {"after_call": True}},
        ],
        "sub": [
            {
                "function": "set_global_variables",
                "args": {"sub_started": True},
            },
            {"function": "return", "args": {"value": "stopped"}},
            {
                "function": "set_global_variables",
                "args": {"sub_finished": True},
            },
        ],
    }
    engine = create_engine(ast)
    state = {}
    engine.run(state)

    assert state.get("sub_started") is True
    assert "sub_finished" not in state
    assert state.get("after_call") is True


# ==========================================
# 5. Scope Behavior Suite (TC-SCOPE)
# ==========================================

def test_tc_scope_01_nested_step_shallow_copy(create_engine):
    """TC-SCOPE-01: Nested step execution uses shallow-copied child state."""
    ast = {
        "main": [
            {"function": "array_create", "target_variable": "out"},
            {
                "function": "foreach",
                "args": {"items": "list", "as": "item"},
                "params": [
                    {
                        "function": "set_variables",
                        "args": {"seen": "item"},
                        "target_variable": "last_seen",
                    }
                ],
            },
        ]
    }
    engine = create_engine(ast)
    state = {"list": [1, 2]}
    engine.run(state)

    # set_variables inside nested scope should not leak to outer scope
    assert "item" not in state
    assert "index" not in state
    assert "seen" not in state
    assert "last_seen" not in state


def test_tc_scope_03_set_global_variables_bypasses_local_scope(create_engine):
    """TC-SCOPE-03: set_global_variables updates root state from nested scope."""
    ast = {
        "main": [
            {
                "function": "foreach",
                "args": {"items": "list", "as": "item"},
                "params": [
                    {
                        "function": "set_global_variables",
                        "args": {"last_processed": "item"},
                    }
                ],
            }
        ]
    }
    engine = create_engine(ast)
    state = {"list": [1, 2]}
    engine.run(state)

    assert state.get("last_processed") == 2


# ==========================================
# 6. Subroutine Suite (TC-COMP)
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


def test_tc_comp_02_missing_component_safety(create_engine):
    """TC-COMP-02: Safe handling when target component is missing"""
    ast = {
        "main": [
            {
                "function": "call_component",
                "args": {"name": "no_such_component"},
            },
            {"function": "set_variables", "args": {"alive": True}},
        ]
    }
    engine = create_engine(ast)
    state = {}
    res = engine.run(state)

    assert state.get("alive") is True
    assert res.status == Status.ERROR
    assert any("Component 'no_such_component' not found" in log for log in res.logs)


# ==========================================
# 8. Validation Failure Suite (TC-VAL)
# ==========================================

def test_tc_val_01_runtime_abort_on_schema_failure(create_engine):
    """TC-VAL-01: Runtime aborts when schema validation fails"""
    ast = {"main": [{"args": {"x": 1}}]}
    engine = create_engine(ast)
    state = {}
    res = engine.run(state)

    assert res.status == Status.ERROR
    assert len(res.logs) > 0