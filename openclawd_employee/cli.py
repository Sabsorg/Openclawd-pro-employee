"""Command-line interface for the Openclawd Employee agent."""

from __future__ import annotations

import argparse
import asyncio
import sys

from openclawd_employee.agent import Agent
from openclawd_employee.config import AgentConfig, LLMConfig


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="openclawd-employee",
        description="Openclawd Pro Employee — autonomous AI agent",
    )
    parser.add_argument("task", nargs="?", help="Task to execute (or use --interactive)")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start an interactive session",
    )
    parser.add_argument("--provider", default="openai", help="LLM provider (openai, anthropic)")
    parser.add_argument("--model", default=None, help="Model name to use")
    parser.add_argument("--max-iterations", type=int, default=50, help="Max agent loop iterations")
    return parser.parse_args(argv)


async def _interactive(agent: Agent) -> None:
    print("Openclawd Employee — interactive mode  (type 'exit' to quit)\n")
    while True:
        try:
            task = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not task or task.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        result = await agent.run(task)
        print(f"\nAgent> {result}\n")


async def _run(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    model = args.model
    if model is None:
        model = "gpt-4o" if args.provider == "openai" else "claude-sonnet-4-20250514"

    config = AgentConfig(
        llm=LLMConfig(provider=args.provider, model=model),
        max_iterations=args.max_iterations,
    )
    agent = Agent(config)

    if args.interactive or args.task is None:
        await _interactive(agent)
    else:
        result = await agent.run(args.task)
        print(result)


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``openclawd-employee`` console script."""
    asyncio.run(_run(argv))


if __name__ == "__main__":
    main()
