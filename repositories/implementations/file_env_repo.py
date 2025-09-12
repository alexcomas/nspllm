from __future__ import annotations

import json
import os
import shutil
from typing import Any, Dict

from repositories.environment_repository import EnvironmentRepository


class FileEnvRepo(EnvironmentRepository):
    def read_json(self, path: str) -> Dict[str, Any]:
        with open(path) as f:
            return json.load(f)

    def write_json(self, path: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def copy_tree(self, src: str, dst: str) -> None:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
