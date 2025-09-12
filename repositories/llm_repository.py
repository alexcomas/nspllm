from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMRepository(ABC):
    """
    Abstraction over LLM backends (OpenAI, local, mock). Implementations should
    encapsulate client setup, retries, and telemetry. Keep the interface narrow
    and testable.
    """

    @abstractmethod
    def chat(self,
             messages: List[Dict[str, str]],
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             **kwargs: Any) -> str:
        """Return the assistant's message content for a chat-style prompt."""
        raise NotImplementedError
