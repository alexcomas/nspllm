from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class EnvironmentService(ABC):
    """
    Handles all environment I/O and conversions (movement files, meta files,
    temp signals). Delegates storage operations to an EnvironmentRepository.
    """

    @abstractmethod
    def read_environment_step(self, sim_code: str, step: int) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_movement_step(self, sim_code: str, step: int, movements: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_meta(self, sim_code: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_meta(self, sim_code: str, meta: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def signal_curr_sim(self, sim_code: str, step: int) -> None:
        raise NotImplementedError
