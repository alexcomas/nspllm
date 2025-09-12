from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ReflectionService(ABC):
    """Creates reflective thoughts and updates memory via repositories."""

    @abstractmethod
    def reflect(self, persona: Any) -> None:
        raise NotImplementedError
