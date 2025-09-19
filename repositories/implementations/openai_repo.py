from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from repositories.llm_repository import LLMRepository


class OpenAIRepo(LLMRepository):
    """
    Thin adapter over the OpenAI v1 Python SDK.

    - Uses `chat.completions.create` with standard messages format
    - Supports dependency injection of a preconfigured client for tests
    - Adds simple retry on transient errors
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        client: Optional[Any] = None,
        model_default: str = "gpt-5-nano-2025-08-07",
        timeout: float = 60.0,
        max_retries: int = 2,
        retry_backoff: float = 1.0,
    ) -> None:
        self.model_default = model_default
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        if client is not None:
            self._client = client
        else:
            # Lazy import so tests without SDK can still import the module when mocked
            from openai import OpenAI  # type: ignore

            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY not set and no api_key provided")
            self._client = OpenAI(api_key=key, timeout=timeout)  # type: ignore[arg-type]

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                # v1 SDK call signature
                completion = self._client.chat.completions.create(
                    model=model or self.model_default,
                    messages=messages,
                    temperature=1,
                    reasoning_effort="minimal",
                    **kwargs,
                )
                # Extract text content
                choice = completion.choices[0]
                # Some SDK versions nest message under `message.content`
                content = getattr(choice, "message", None)
                if content is not None:
                    return getattr(choice.message, "content", "")
                # Fallback if content is on `text`
                return getattr(choice, "text", "")
            except Exception as e:  # noqa: BLE001 - we want a broad retry here
                last_err = e
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_backoff * (2 ** attempt))
        # Out of retries
        assert last_err is not None
        raise last_err
