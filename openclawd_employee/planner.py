"""Planner – breaks high-level tasks into actionable steps."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from openclawd_employee.llm.base import LLMProvider

PLANNING_PROMPT = """\
You are a planning module for an autonomous AI agent.  Given the user's goal
and the tools available, produce a JSON array of step objects.  Each step has:
  - "description": a short description of the step
  - "tool": the tool name to use (or "respond" to give a final answer)
  - "args": a dict of arguments to pass to the tool

Return ONLY valid JSON – no markdown fences, no commentary.
"""


@dataclass
class Step:
    """A single planned action."""

    description: str
    tool: str
    args: dict[str, Any] = field(default_factory=dict)


async def create_plan(
    goal: str,
    tool_schemas: list[dict[str, Any]],
    llm: LLMProvider,
    context: str = "",
) -> list[Step]:
    """Ask the LLM to decompose *goal* into a list of Steps."""
    tool_list = "\n".join(
        f"- {s['function']['name']}: {s['function']['description']}"
        for s in tool_schemas
    )
    user_content = f"Tools available:\n{tool_list}\n\nGoal: {goal}"
    if context:
        user_content += f"\n\nContext so far:\n{context}"

    messages = [
        {"role": "system", "content": PLANNING_PROMPT},
        {"role": "user", "content": user_content},
    ]
    response = await llm.chat(messages, temperature=0.0)
    raw = response.get("content", "[]")

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return [Step(description="Execute goal directly", tool="respond", args={"text": raw})]

    steps: list[Step] = []
    for item in items:
        steps.append(
            Step(
                description=item.get("description", ""),
                tool=item.get("tool", "respond"),
                args=item.get("args", {}),
            )
        )
    return steps
