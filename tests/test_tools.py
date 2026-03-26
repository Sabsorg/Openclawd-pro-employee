"""Tests for the tool registry and base tool interface."""

from __future__ import annotations

import pytest

from openclawd_employee.tools.base import Tool, ToolRegistry
from typing import Any


class DummyTool(Tool):
    """A minimal tool for testing."""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "A dummy tool for tests."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"msg": {"type": "string"}},
            "required": ["msg"],
        }

    async def run(self, **kwargs: Any) -> str:
        return f"echo: {kwargs.get('msg', '')}"


class TestToolRegistry:
    def test_register_and_get(self) -> None:
        registry = ToolRegistry()
        tool = DummyTool()
        registry.register(tool)
        assert registry.get("dummy") is tool

    def test_get_unknown_returns_none(self) -> None:
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_list_tools(self) -> None:
        registry = ToolRegistry()
        registry.register(DummyTool())
        assert len(registry.list_tools()) == 1

    def test_to_schemas(self) -> None:
        registry = ToolRegistry()
        registry.register(DummyTool())
        schemas = registry.to_schemas()
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"
        assert schemas[0]["function"]["name"] == "dummy"

    def test_parse_arguments_dict(self) -> None:
        assert ToolRegistry.parse_arguments({"a": 1}) == {"a": 1}

    def test_parse_arguments_json_string(self) -> None:
        assert ToolRegistry.parse_arguments('{"a": 1}') == {"a": 1}

    def test_parse_arguments_invalid(self) -> None:
        assert ToolRegistry.parse_arguments("not json") == {}

    def test_parse_arguments_non_dict_json(self) -> None:
        """Valid JSON that is not an object should return empty dict."""
        assert ToolRegistry.parse_arguments("[]") == {}
        assert ToolRegistry.parse_arguments('"text"') == {}
        assert ToolRegistry.parse_arguments("null") == {}


@pytest.mark.asyncio
async def test_dummy_tool_run() -> None:
    tool = DummyTool()
    result = await tool.run(msg="hello")
    assert result == "echo: hello"
