# Writing Custom Functions

You can extend `flitflow` by subclassing `BaseFunction` to integrate custom Python logic or external APIs into your AST scripts.

## Creating a Custom Function

```python
from typing import Any
from flitflow import BaseFunction, RuntimeResult, Status

class HttpGetFunction(BaseFunction):
    """Custom handler to perform HTTP GET requests."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        url = args.get("url")
        if not url:
            return RuntimeResult(
                status=Status.ERROR,
                value=None,
                logs=["'url' argument is required"],
            )

        # Execution logic (mocked)
        mock_response = {"status": 200, "data": "OK"}

        return RuntimeResult(
            status=Status.SUCCESS,
            value=mock_response,
        )
```

## Registering and Calling

```python
from flitflow import RuntimeEngine

ast = {
    "main": [
        {
            "function": "http_get",
            "args": {"url": "[https://api.example.com](https://api.example.com)"},
            "target_variable": "api_result"
        }
    ]
}

engine = RuntimeEngine(ast)
engine.register_function("http_get", HttpGetFunction())

state = {}
engine.run(state)

print(state["api_result"])  # Output: {'status': 200, 'data': 'OK'}
```
