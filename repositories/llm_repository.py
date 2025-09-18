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

    # High-level convenience methods defined by the contract. Default
    # implementations delegate to `chat` to avoid breaking subclasses.
    def generate(self, prompt: str, **kwargs: Any) -> str:
        messages = kwargs.pop("messages", None)
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def structured(self, prompt: str, schema: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        _ = schema  # schema is advisory in the default adapter
        text = self.generate(prompt, **kwargs)
        return {"text": text}

    def call_function(self, prompt: str, functions: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        _ = functions  # functions is advisory in the default adapter
        text = self.generate(prompt, **kwargs)
        return {"text": text}
