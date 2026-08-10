from typing import Any
from flitflow.base import BaseFunction, RuntimeResult, Status


class ArrayCreateFunction(BaseFunction):
    """`array_create`: Create a new empty array."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        return RuntimeResult(status=Status.SUCCESS, value=[])


class ArrayPushFunction(BaseFunction):
    """`array_push`: Append an element to the end of an array."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        target_array = args.get("array")
        val = args.get("value")

        # Resolve the array argument when it is passed as a variable-name string and exists in state
        if isinstance(target_array, str) and target_array in state:
            arr = state[target_array]
        else:
            arr = target_array

        if isinstance(arr, list):
            arr.append(val)
            return RuntimeResult(status=Status.SUCCESS, value=arr)

        # Always safe: if the target is not a list, emit a warning log and return NULL
        return RuntimeResult(
            status=Status.WARNING,
            value=None,
            logs=[f"array_push target '{target_array}' is not a valid list."],
        )


class ArrayGetFunction(BaseFunction):
    """`array_get`: Retrieve an element from an array at the specified index (out-of-bounds access returns NULL safely)."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        target_array = args.get("array")
        index = args.get("index")

        if isinstance(target_array, str) and target_array in state:
            arr = state[target_array]
        else:
            arr = target_array

        if isinstance(arr, list) and isinstance(index, int):
            if 0 <= index < len(arr):
                return RuntimeResult(status=Status.SUCCESS, value=arr[index])

        # TC-SAFE-02 / SPEC 2.3.10: Return None (NULL) safely for out-of-bounds or invalid types
        return RuntimeResult(
            status=Status.SUCCESS,
            value=None,
            logs=[
                f"array_get out-of-bounds or invalid type: array={target_array}, index={index}"
            ],
        )


class ArrayLengthFunction(BaseFunction):
    """`array_length`: Get the number of elements in an array."""

    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        target_array = args.get("array")

        if isinstance(target_array, str) and target_array in state:
            arr = state[target_array]
        else:
            arr = target_array

        if isinstance(arr, list):
            return RuntimeResult(status=Status.SUCCESS, value=len(arr))

        # SPEC 2.3.11: Safely return None (NULL) for invalid types
        return RuntimeResult(
            status=Status.WARNING,
            value=None,
            logs=[f"array_length target '{target_array}' is not a valid list."],
        )
