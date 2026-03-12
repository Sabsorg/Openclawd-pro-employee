"""File-system tools — read, write, and list directories."""

from __future__ import annotations

import os
from typing import Any

from openclawd_employee.tools.base import Tool


class ReadFileTool(Tool):
    """Read the contents of a file."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path and return its text."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
            },
            "required": ["path"],
        }

    async def run(self, **kwargs: Any) -> str:
        path: str = kwargs["path"]
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError as exc:
            return f"Error reading file: {exc}"


class WriteFileTool(Tool):
    """Create or overwrite a file with the given content."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file, creating parent directories if needed."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write.",
                },
            },
            "required": ["path", "content"],
        }

    async def run(self, **kwargs: Any) -> str:
        path: str = kwargs["path"]
        content: str = kwargs["content"]
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            return f"Successfully wrote {len(content)} characters to {path}"
        except OSError as exc:
            return f"Error writing file: {exc}"


class ListDirectoryTool(Tool):
    """List files and directories at a given path."""

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List files and sub-directories at the specified path."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to '.'",
                    "default": ".",
                },
            },
        }

    async def run(self, **kwargs: Any) -> str:
        path: str = kwargs.get("path", ".")
        try:
            entries = sorted(os.listdir(path))
            if not entries:
                return f"{path} is empty."
            return "\n".join(entries)
        except OSError as exc:
            return f"Error listing directory: {exc}"
