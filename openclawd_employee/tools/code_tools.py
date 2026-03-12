"""Code analysis / execution tools."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from openclawd_employee.tools.base import Tool


class PythonExecTool(Tool):
    """Execute a snippet of Python code in a subprocess and capture output.

    The code runs in a **separate process** with a configurable timeout to
    prevent the agent loop from hanging.  This is *not* a full sandbox —
    the subprocess still has filesystem and network access — so only
    enable this tool in trusted environments.
    """

    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "python_exec"

    @property
    def description(self) -> str:
        return (
            "Execute a Python code snippet in a subprocess and return its "
            "printed output.  Execution is time-limited (default 30 s).  "
            "WARNING: not a full sandbox — only enable in trusted environments."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source code to execute.",
                },
            },
            "required": ["code"],
        }

    async def run(self, **kwargs: Any) -> str:
        code: str = kwargs["code"]
        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self._timeout
            )
            parts = [s.decode(errors="replace") for s in (stdout, stderr) if s]
            output = "\n".join(parts).strip()
            return output if output else "(no output)"
        except asyncio.TimeoutError:
            if proc is not None:
                try:
                    proc.kill()
                    await proc.wait()
                except (ProcessLookupError, OSError):
                    pass
            return f"Execution timed out after {self._timeout}s"
        except Exception as exc:  # noqa: BLE001
            return f"Execution error: {exc}"
