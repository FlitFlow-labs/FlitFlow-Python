from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional


class Signal(str, Enum):
    NONE = "NONE"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class RuntimeResult:
    status: Status = Status.SUCCESS
    signal: Signal = Signal.NONE
    value: Any = None
    logs: list[str] = field(default_factory=list)

    def merge(self, other: "RuntimeResult") -> None:
        """Helper to merge logs and status from another execution result."""
        self.logs.extend(other.logs)
        if other.status == Status.ERROR:
            self.status = Status.ERROR
        elif other.status == Status.WARNING and self.status != Status.ERROR:
            self.status = Status.WARNING


class BaseFunction(ABC):
    """Base class for all FlitFlow functions."""

    @abstractmethod
    def execute(
        self,
        args: dict[str, Any],
        params: Any,
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        """Function-specific logic (receives pre-evaluated args and raw params)."""
        pass

    def run(
        self,
        raw_args: dict[str, Any],
        params: Any,
        target_variable: Optional[str],
        state: dict[str, Any],
        engine: Any,
    ) -> RuntimeResult:
        """Common execution pipeline aligned with SPEC 1.2.3."""
        # 1. Argument Pre-Evaluation (args)
        evaluated_args = engine.evaluate_args(raw_args, state) if raw_args else {}

        # 2. Invocation (execute)
        result = self.execute(evaluated_args, params, state, engine)

        # 3. Target Binding (target_variable)
        if target_variable and result.signal == Signal.NONE:
            state[target_variable] = result.value

        return result
