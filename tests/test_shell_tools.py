"""Tests for the shell tool."""

from __future__ import annotations

import pytest

from openclawd_employee.tools.shell_tools import ShellTool


@pytest.mark.asyncio
async def test_shell_echo() -> None:
    tool = ShellTool()
    result = await tool.run(command="echo hello")
    assert "hello" in result
    assert "exit code 0" in result


@pytest.mark.asyncio
async def test_shell_exit_code() -> None:
    tool = ShellTool()
    result = await tool.run(command="exit 1")
    assert "exit code 1" in result
