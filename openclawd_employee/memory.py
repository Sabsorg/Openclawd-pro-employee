"""Memory / state management for agent context across steps."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory record."""

    role: str  # "user", "assistant", "tool", "system"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Memory:
    """Manages conversational and working memory for an agent run.

    Provides short-term (conversation history) and long-term (facts /
    key-value store) memory that persists across planning iterations.
    """

    def __init__(self, system_prompt: str = "") -> None:
        self._conversation: list[MemoryEntry] = []
        self._facts: dict[str, str] = {}
        if system_prompt:
            self.add("system", system_prompt)

    # -- Conversation (short-term) memory --------------------------------

    def add(self, role: str, content: str, **metadata: Any) -> None:
        """Append a message to conversation history."""
        self._conversation.append(
            MemoryEntry(role=role, content=content, metadata=metadata)
        )

    @property
    def conversation(self) -> list[MemoryEntry]:
        """Return the full conversation history."""
        return list(self._conversation)

    def to_messages(self) -> list[dict[str, str]]:
        """Serialise conversation history to the OpenAI message format."""
        return [{"role": e.role, "content": e.content} for e in self._conversation]

    # -- Facts (long-term) memory ----------------------------------------

    def store_fact(self, key: str, value: str) -> None:
        """Store or update a named fact."""
        self._facts[key] = value

    def get_fact(self, key: str, default: str = "") -> str:
        """Retrieve a stored fact by key."""
        return self._facts.get(key, default)

    @property
    def facts(self) -> dict[str, str]:
        """Return all stored facts."""
        return dict(self._facts)

    def clear(self) -> None:
        """Reset all memory."""
        self._conversation.clear()
        self._facts.clear()
