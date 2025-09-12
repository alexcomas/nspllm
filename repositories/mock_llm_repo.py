from __future__ import annotations

from typing import Any, Dict, List, Optional

from .llm_repository import LLMRepository


class MockLLMRepository(LLMRepository):
    def chat(self,
             messages: List[Dict[str, str]],
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             **kwargs: Any) -> str:
        # Deterministic echo: return last user content or a canned message
        for m in reversed(messages):
            if m.get("role") == "user":
                return f"MOCK:{m.get('content','')}"
        return "MOCK:OK"
