from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class DialogueService(ABC):
    """Generates dialogue utterances and manages chat state for personas."""

    @abstractmethod
    def maybe_start_conversation(self, persona: Any, others: Dict[str, Any], context: Dict[str, Any]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def next_utterance(self, persona: Any, partner: Any, context: Dict[str, Any]) -> str:
        raise NotImplementedError
