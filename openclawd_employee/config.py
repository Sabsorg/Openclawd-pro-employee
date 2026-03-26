"""Configuration management for the Openclawd Employee agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMConfig:
    """Settings for the backing LLM provider."""

    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str | None = None
    temperature: float = 0.0
    max_tokens: int = 4096

    def __post_init__(self) -> None:
        if not self.api_key:
            env_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }
            env_var = env_map.get(self.provider, "LLM_API_KEY")
            self.api_key = os.environ.get(env_var, "")


@dataclass
class AgentConfig:
    """Top-level configuration for an Openclawd Employee agent."""

    name: str = "openclawd-employee"
    description: str = "An autonomous AI employee that can accomplish any workflow."
    max_iterations: int = 50
    llm: LLMConfig = field(default_factory=LLMConfig)
    allowed_tools: list[str] = field(default_factory=list)
    # Extra provider-specific or user-defined settings
    extra: dict[str, Any] = field(default_factory=dict)
