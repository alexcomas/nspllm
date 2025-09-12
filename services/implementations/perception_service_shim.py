from __future__ import annotations

import logging
from typing import Any, List

from services.perception_service import PerceptionService


class PerceptionServiceShim(PerceptionService):
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._log = logger or logging.getLogger(__name__)

    def perceive(self, persona: Any, maze: Any) -> List[Any]:
        self._log.debug(
            "PerceptionServiceShim.perceive called",
            extra={"persona": getattr(persona, "name", None)},
        )

        from reverie.backend_server.persona.cognitive_modules.perceive import (
            perceive as _legacy_perceive,
        )

        return _legacy_perceive(persona, maze)
