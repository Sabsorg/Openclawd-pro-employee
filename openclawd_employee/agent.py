"""Core agent — the autonomous loop that plans, acts, and observes."""

from __future__ import annotations

import logging
from typing import Any

from openclawd_employee.config import AgentConfig
from openclawd_employee.executor import execute_tool_calls
from openclawd_employee.llm.base import LLMProvider
from openclawd_employee.llm.providers import AnthropicProvider, OpenAIProvider
from openclawd_employee.memory import Memory
from openclawd_employee.tools.base import ToolRegistry
from openclawd_employee.tools.code_tools import PythonExecTool
from openclawd_employee.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from openclawd_employee.tools.shell_tools import ShellTool
from openclawd_employee.tools.web_tools import HttpRequestTool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are **Openclawd Employee**, an autonomous AI agent that can accomplish
any workflow.  You have access to tools for file I/O, shell commands, HTTP
requests, and Python code execution.

When given a task:
1. **Plan** — think through the steps needed.
2. **Act** — call the appropriate tools to carry out each step.
3. **Observe** — review the tool output to decide the next action.
4. **Repeat** until the task is complete, then respond with the final result.

Be concise, accurate, and proactive.  If something fails, diagnose and retry.
"""


def _build_registry(config: AgentConfig) -> ToolRegistry:
    """Instantiate all built-in tools and register them."""
    registry = ToolRegistry()
    all_tools = [
        ReadFileTool(),
        WriteFileTool(),
        ListDirectoryTool(),
        ShellTool(),
        HttpRequestTool(),
        PythonExecTool(),
    ]
    allowed = set(config.allowed_tools) if config.allowed_tools else None
    for tool in all_tools:
        if allowed is None or tool.name in allowed:
            registry.register(tool)
    return registry


def _build_llm(config: AgentConfig) -> LLMProvider:
    """Return the LLM provider specified in the config."""
    if config.llm.provider == "anthropic":
        return AnthropicProvider(
            api_key=config.llm.api_key,
            model=config.llm.model,
        )
    return OpenAIProvider(
        api_key=config.llm.api_key,
        model=config.llm.model,
        base_url=config.llm.base_url,
    )


class Agent:
    """The Openclawd Employee agent.

    Implements a ReAct-style (Reason + Act) loop: the LLM decides which
    tool to call, the executor runs it, and the result is fed back until
    the model produces a final answer or the iteration limit is reached.
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.registry = _build_registry(self.config)
        self.llm = _build_llm(self.config)
        self.memory = Memory(system_prompt=SYSTEM_PROMPT)

    async def run(self, task: str) -> str:
        """Execute *task* autonomously and return the final answer."""
        self.memory.add("user", task)
        logger.info("Agent received task: %s", task)

        for iteration in range(1, self.config.max_iterations + 1):
            logger.debug("Iteration %d", iteration)

            response = await self.llm.chat(
                messages=self.memory.to_messages(),
                tools=self.registry.to_schemas() or None,
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens,
            )

            content: str = response.get("content", "")
            tool_calls: list[dict[str, Any]] = response.get("tool_calls", [])

            if not tool_calls:
                # The model produced a final textual answer.
                self.memory.add("assistant", content)
                logger.info("Agent finished after %d iterations.", iteration)
                return content

            # Record the assistant message (may include partial text).
            self.memory.add("assistant", content, tool_calls=tool_calls)

            # Execute every tool call and feed results back.
            results = await execute_tool_calls(tool_calls, self.registry)
            for result in results:
                self.memory.add(
                    "tool",
                    result["content"],
                    tool_call_id=result["tool_call_id"],
                )

        return "Reached maximum iterations without a final answer."
