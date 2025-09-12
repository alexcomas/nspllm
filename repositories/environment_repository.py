from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class EnvironmentRepository(ABC):
    """Abstracts storage operations for environment and simulation state."""

    @abstractmethod
    def read_json(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_json(self, path: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def copy_tree(self, src: str, dst: str) -> None:
        raise NotImplementedError
