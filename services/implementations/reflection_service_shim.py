from __future__ import annotations

import logging
from typing import Any

from services.reflection_service import ReflectionService


class ReflectionServiceShim(ReflectionService):
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._log = logger or logging.getLogger(__name__)

    def reflect(self, persona: Any) -> None:
        self._log.debug("ReflectionServiceShim.reflect called", extra={"persona": getattr(persona, "name", None)})
        from reverie.backend_server.persona.cognitive_modules.reflect import run_reflect as _legacy_reflect

        _legacy_reflect(persona)
