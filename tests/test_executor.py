"""Tests for the executor module."""

from __future__ import annotations

import pytest

from openclawd_employee.executor import execute_tool_calls
from openclawd_employee.tools.base import ToolRegistry, Tool
from typing import Any


class EchoTool(Tool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echoes input."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"text": {"type": "string"}}}

    async def run(self, **kwargs: Any) -> str:
        return kwargs.get("text", "")


@pytest.mark.asyncio
async def test_execute_tool_calls() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())
    calls = [
        {
            "id": "call_1",
            "function": {"name": "echo", "arguments": '{"text": "hi"}'},
        }
    ]
    results = await execute_tool_calls(calls, registry)
    assert len(results) == 1
    assert results[0]["content"] == "hi"
    assert results[0]["tool_call_id"] == "call_1"


@pytest.mark.asyncio
async def test_execute_unknown_tool() -> None:
    registry = ToolRegistry()
    calls = [
        {
            "id": "call_2",
            "function": {"name": "nonexistent", "arguments": "{}"},
        }
    ]
    results = await execute_tool_calls(calls, registry)
    assert "Unknown tool" in results[0]["content"]
