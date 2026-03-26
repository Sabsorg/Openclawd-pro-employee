"""Executor – runs tool calls returned by the LLM and collects results."""

from __future__ import annotations

from typing import Any

from openclawd_employee.tools.base import ToolRegistry


async def execute_tool_calls(
    tool_calls: list[dict[str, Any]],
    registry: ToolRegistry,
) -> list[dict[str, Any]]:
    """Execute each tool call and return a list of result messages.

    Each result dict is ready to be appended to the conversation as a
    ``tool`` message (OpenAI format).
    """
    results: list[dict[str, Any]] = []
    for tc in tool_calls:
        fn_name = tc["function"]["name"]
        raw_args = tc["function"]["arguments"]
        parsed = ToolRegistry.parse_arguments(raw_args)

        tool = registry.get(fn_name)
        if tool is None:
            output = f"Unknown tool: {fn_name}"
        else:
            try:
                output = await tool.run(**parsed)
            except Exception as exc:  # noqa: BLE001
                output = f"Tool {fn_name} failed with error: {exc!r}"

        results.append(
            {
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": output,
            }
        )
    return results
