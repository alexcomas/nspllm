from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


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
