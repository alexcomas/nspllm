from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

from repositories.llm_repository import LLMRepository
from services.environment_service import EnvironmentService
from services.planning_service import PlanningService


class PlanningServiceShim(PlanningService):
    """
    Shim implementation that delegates to the existing legacy planning logic
    in `reverie.backend_server.persona.cognitive_modules.plan` to preserve
    behavior while we refactor incrementally. Dependencies are accepted for
    future use but not used yet.
    """

    def __init__(
        self,
        llm_repo: LLMRepository,
        env_service: EnvironmentService,
        logger: logging.Logger | None = None,
    ) -> None:
        self._llm_repo = llm_repo
        self._env_service = env_service
        self._log = logger or logging.getLogger(__name__)

    def plan(
        self,
        persona: Any,
        maze: Any,
        personas: Dict[str, Any],
        new_day: bool | str,
        retrieved: Dict[str, Dict[str, Any]],
    ) -> Tuple[int, int] | Any:
        self._log.debug(
            "PlanningServiceShim.plan called",
            extra={
                "persona": getattr(persona, "name", None),
                "new_day": new_day,
                "retrieved_keys": list(retrieved.keys()) if isinstance(retrieved, dict) else None,
            },
        )

        # Delegate to legacy implementation to maintain behavior.
        from reverie.backend_server.persona.cognitive_modules.plan import (
            plan as _legacy_plan,
        )

        return _legacy_plan(persona, maze, personas, new_day, retrieved)
