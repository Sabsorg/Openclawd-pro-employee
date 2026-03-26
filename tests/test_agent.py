"""Tests for agent construction and tool registration."""

from __future__ import annotations

from openclawd_employee.agent import Agent, _build_registry
from openclawd_employee.config import AgentConfig


class TestAgentInit:
    def test_default_agent_has_all_tools(self) -> None:
        agent = Agent()
        tool_names = {t.name for t in agent.registry.list_tools()}
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "shell" in tool_names
        assert "http_request" in tool_names
        assert "python_exec" in tool_names
        assert "list_directory" in tool_names

    def test_allowed_tools_filter(self) -> None:
        config = AgentConfig(allowed_tools=["shell"])
        registry = _build_registry(config)
        assert registry.get("shell") is not None
        assert registry.get("read_file") is None

    def test_memory_has_system_prompt(self) -> None:
        agent = Agent()
        assert len(agent.memory.conversation) == 1
        assert agent.memory.conversation[0].role == "system"
