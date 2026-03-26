"""Base tool interface and tool registry."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Abstract base class for all agent tools.

    Every tool exposes a *name*, a human-readable *description*, and a
    JSON-schema *parameters* dict so the LLM can decide when and how to
    invoke it.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier (snake_case)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short explanation of what the tool does."""

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON-schema describing accepted parameters."""

    @abstractmethod
    async def run(self, **kwargs: Any) -> str:
        """Execute the tool and return a string result."""

    def to_function_schema(self) -> dict[str, Any]:
        """Return the OpenAI-style function/tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Central registry that maps tool names to *Tool* instances."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def to_schemas(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for all registered tools."""
        return [t.to_function_schema() for t in self._tools.values()]

    @staticmethod
    def parse_arguments(raw: str | dict[str, Any]) -> dict[str, Any]:
        """Safely parse tool-call arguments from the LLM response."""
        if isinstance(raw, dict):
            return raw
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except (json.JSONDecodeError, TypeError):
            return {}
