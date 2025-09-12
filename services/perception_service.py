from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class PerceptionService(ABC):
    """Produces structured perceptions for a persona from the environment."""

    @abstractmethod
    def perceive(self, persona: Any, maze: Any) -> List[Any]:
        raise NotImplementedError
