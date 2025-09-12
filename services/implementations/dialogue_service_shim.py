from __future__ import annotations

import logging
from typing import Any, Dict

from repositories.llm_repository import LLMRepository
from services.dialogue_service import DialogueService
from services.environment_service import EnvironmentService


class DialogueServiceShim(DialogueService):
    """
    Shim for dialogue that delegates to legacy converse module to preserve
    behavior while introducing DI boundaries.
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

    def maybe_start_conversation(self, persona: Any, others: Dict[str, Any], context: Dict[str, Any]) -> bool:
        # For now, we do not change legacy triggering heuristics. We simply
        # return True if legacy plan module would decide to chat; this shim
        # only prepares the ground for future logic.
        # We conservatively return False here; start will be handled when
        # planning decides to chat in legacy flow.
        self._log.debug("DialogueServiceShim.maybe_start_conversation called", extra={"persona": getattr(persona, "name", None)})
        return False

    def next_utterance(self, persona: Any, partner: Any, context: Dict[str, Any]) -> str:
        self._log.debug(
            "DialogueServiceShim.next_utterance called",
            extra={"persona": getattr(persona, "name", None), "partner": getattr(partner, "name", None)},
        )

        from reverie.backend_server.persona.cognitive_modules.converse import (
            agent_chat_v1 as _legacy_agent_chat_v1,
        )

        # The legacy function returns a list of lines; we join to a string for
        # a simple utterance. Caller can split if multi-turn is desired.
        lines = _legacy_agent_chat_v1(context.get("maze"), persona, partner)
        if isinstance(lines, list):
            return "\n".join(str(x) for x in lines)
        return str(lines)
