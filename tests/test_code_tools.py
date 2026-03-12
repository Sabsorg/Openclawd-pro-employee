"""Tests for the Python execution tool."""

from __future__ import annotations

import pytest

from openclawd_employee.tools.code_tools import PythonExecTool


@pytest.mark.asyncio
async def test_python_exec_print() -> None:
    tool = PythonExecTool()
    result = await tool.run(code="print(2 + 2)")
    assert "4" in result


@pytest.mark.asyncio
async def test_python_exec_no_output() -> None:
    tool = PythonExecTool()
    result = await tool.run(code="x = 1")
    assert result == "(no output)"


@pytest.mark.asyncio
async def test_python_exec_error() -> None:
    tool = PythonExecTool()
    result = await tool.run(code="raise ValueError('boom')")
    assert "boom" in result


@pytest.mark.asyncio
async def test_python_exec_timeout() -> None:
    tool = PythonExecTool(timeout=1)
    result = await tool.run(code="import time; time.sleep(10)")
    assert "timed out" in result
