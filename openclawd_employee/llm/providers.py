"""Concrete LLM provider implementations."""

from __future__ import annotations

import json
from typing import Any

from openclawd_employee.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Provider that wraps the OpenAI (or compatible) chat API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls: list[dict[str, Any]] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                )

        return {
            "content": message.content or "",
            "tool_calls": tool_calls,
            "finish_reason": choice.finish_reason,
        }


class AnthropicProvider(LLMProvider):
    """Provider that wraps the Anthropic messages API.

    Translates Anthropic's tool-use format into the common schema used
    by the agent loop so the rest of the codebase stays provider-agnostic.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self._api_key = api_key
        self._model = model

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        import httpx

        # Separate the system prompt from conversation messages.
        system_text = ""
        conversation: list[dict[str, str]] = []
        for msg in messages:
            if msg["role"] == "system":
                system_text += msg["content"] + "\n"
            else:
                conversation.append(msg)

        # Build Anthropic-style tool definitions.
        ant_tools: list[dict[str, Any]] = []
        if tools:
            for t in tools:
                fn = t.get("function", {})
                ant_tools.append(
                    {
                        "name": fn.get("name", ""),
                        "description": fn.get("description", ""),
                        "input_schema": fn.get("parameters", {}),
                    }
                )

        body: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": conversation,
        }
        if system_text.strip():
            body["system"] = system_text.strip()
        if ant_tools:
            body["tools"] = ant_tools

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        # Normalise the response.
        content_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for block in data.get("content", []):
            if block["type"] == "text":
                content_parts.append(block["text"])
            elif block["type"] == "tool_use":
                tool_calls.append(
                    {
                        "id": block["id"],
                        "function": {
                            "name": block["name"],
                            "arguments": json.dumps(block["input"]),
                        },
                    }
                )

        return {
            "content": "\n".join(content_parts),
            "tool_calls": tool_calls,
            "finish_reason": data.get("stop_reason", "end_turn"),
        }
