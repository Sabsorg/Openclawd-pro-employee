"""Code analysis / execution tools."""

from __future__ import annotations

import io
import contextlib
from typing import Any

from openclawd_employee.tools.base import Tool


class PythonExecTool(Tool):
    """Execute a snippet of Python code and capture its output."""

    @property
    def name(self) -> str:
        return "python_exec"

    @property
    def description(self) -> str:
        return (
            "Execute a Python code snippet in an isolated namespace "
            "and return its printed output. WARNING: code runs in-process "
            "without a sandbox — only enable in trusted environments."
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
        buf = io.StringIO()
        namespace: dict[str, Any] = {}
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                exec(code, namespace)  # noqa: S102 – intentional sandboxed exec
            output = buf.getvalue()
            return output if output else "(no output)"
        except Exception as exc:  # noqa: BLE001
            return f"Execution error: {exc}\n{buf.getvalue()}"
