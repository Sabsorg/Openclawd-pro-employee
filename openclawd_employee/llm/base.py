"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Vendor-neutral interface for calling a large language model."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Send a chat-completion request.

        Returns a dict with at least:
        - ``content``: The assistant's text reply (may be empty when tool
          calls are returned).
        - ``tool_calls``: A list of tool-call dicts, each with ``id``,
          ``function.name``, and ``function.arguments``.
        - ``finish_reason``: Why the model stopped (``stop``, ``tool_calls``,
          etc.).
        """
