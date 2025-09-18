from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Protocol


class PlanningService(ABC):
    """
    Plans high-level and short-term actions for a persona, based on retrieved
    memory and perception. Implementations must be pure with respect to I/O
    (delegate to repositories/services) and side-effect free beyond returned values.
    """

    @abstractmethod
    def plan(self,
             persona: Any,
             maze: Any,
             personas: Dict[str, Any],
             new_day: bool | str,
             retrieved: Dict[str, Dict[str, Any]]) -> Tuple[int, int] | Any:
        """
        Compute target action/address for the persona. The concrete return type
        matches existing `persona.plan` expectations to avoid breakage.
        """
        raise NotImplementedError


class PlanningError(Exception):
    """Domain-specific error for planning failures."""


class PlanningModule(Protocol):
    """Stable interface for planning modules used by the engine."""

    def plan(
        self,
        persona: Any,
        maze: Any,
        personas: Dict[str, Any],
        new_day: bool | str,
        retrieved: Dict[str, Dict[str, Any]],
    ) -> Tuple[int, int] | Any:  # pragma: no cover - interface declaration only
        ...

    def replan(
        self,
        persona: Any,
        maze: Any,
        personas: Dict[str, Any],
        reason: str | None = None,
    ) -> Tuple[int, int] | Any:  # pragma: no cover - interface declaration only
        ...

    def next_action(
        self,
        persona: Any,
        context: Dict[str, Any],
    ) -> Any:  # pragma: no cover - interface declaration only
        ...
