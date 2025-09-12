from __future__ import annotations

from typing import Any, Dict

from .environment_service import EnvironmentService
from repositories.environment_repository import EnvironmentRepository


class FileSystemEnvironmentService(EnvironmentService):
    def __init__(self, repo: EnvironmentRepository, fs_storage: str, fs_temp_storage: str):
        self.repo = repo
        self.fs_storage = fs_storage
        self.fs_temp_storage = fs_temp_storage

    def _sim_folder(self, sim_code: str) -> str:
        return f"{self.fs_storage}/{sim_code}"

    def read_environment_step(self, sim_code: str, step: int) -> Dict[str, Any]:
        path = f"{self._sim_folder(sim_code)}/environment/{step}.json"
        return self.repo.read_json(path)

    def write_movement_step(self, sim_code: str, step: int, movements: Dict[str, Any]) -> None:
        path = f"{self._sim_folder(sim_code)}/movement/{step}.json"
        self.repo.write_json(path, movements)

    def read_meta(self, sim_code: str) -> Dict[str, Any]:
        path = f"{self._sim_folder(sim_code)}/reverie/meta.json"
        return self.repo.read_json(path)

    def write_meta(self, sim_code: str, meta: Dict[str, Any]) -> None:
        path = f"{self._sim_folder(sim_code)}/reverie/meta.json"
        self.repo.write_json(path, meta)

    def signal_curr_sim(self, sim_code: str, step: int) -> None:
        self.repo.write_json(f"{self.fs_temp_storage}/curr_sim_code.json", {"sim_code": sim_code})
        self.repo.write_json(f"{self.fs_temp_storage}/curr_step.json", {"step": step})
