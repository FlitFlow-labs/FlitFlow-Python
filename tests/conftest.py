import pytest
from flitflow.engine import RuntimeEngine
from flitflow.functions import register_builtin_functions


@pytest.fixture
def create_engine():
    """Fixture that creates an engine with built-in functions already registered."""
    def _factory(ast):
        engine = RuntimeEngine(ast)
        register_builtin_functions(engine)
        return engine

    return _factory
