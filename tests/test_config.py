"""Tests for the configuration module."""

from openclawd_employee.config import AgentConfig, LLMConfig


class TestLLMConfig:
    def test_defaults(self) -> None:
        cfg = LLMConfig()
        assert cfg.provider == "openai"
        assert cfg.model == "gpt-4o"
        assert cfg.temperature == 0.0

    def test_custom_values(self) -> None:
        cfg = LLMConfig(provider="anthropic", model="claude-sonnet-4-20250514", temperature=0.5)
        assert cfg.provider == "anthropic"
        assert cfg.model == "claude-sonnet-4-20250514"


class TestAgentConfig:
    def test_defaults(self) -> None:
        cfg = AgentConfig()
        assert cfg.name == "openclawd-employee"
        assert cfg.max_iterations == 50
        assert isinstance(cfg.llm, LLMConfig)

    def test_allowed_tools(self) -> None:
        cfg = AgentConfig(allowed_tools=["shell", "read_file"])
        assert cfg.allowed_tools == ["shell", "read_file"]
