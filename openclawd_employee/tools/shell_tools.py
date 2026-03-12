"""Shell command execution tool."""

from __future__ import annotations

import asyncio
import shlex
from typing import Any

from openclawd_employee.tools.base import Tool


class ShellTool(Tool):
    """Execute a shell command and return its output."""

    def __init__(self, timeout: int = 120) -> None:
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return (
            "Run a shell command and return stdout/stderr. "
            "Use for build, test, git, or any CLI task."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
            },
            "required": ["command"],
        }

    async def run(self, **kwargs: Any) -> str:
        command: str = kwargs["command"]
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self._timeout
            )
            parts: list[str] = []
            if stdout:
                parts.append(stdout.decode(errors="replace"))
            if stderr:
                parts.append(stderr.decode(errors="replace"))
            parts.append(f"(exit code {proc.returncode})")
            return "\n".join(parts)
        except asyncio.TimeoutError:
            return f"Command timed out after {self._timeout}s"
        except OSError as exc:
            return f"Error executing command: {exc}"
