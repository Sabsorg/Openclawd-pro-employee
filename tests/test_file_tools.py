"""Tests for built-in file tools."""

from __future__ import annotations

import os
import tempfile

import pytest

from openclawd_employee.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)


@pytest.mark.asyncio
async def test_read_file() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        path = f.name
    try:
        tool = ReadFileTool()
        result = await tool.run(path=path)
        assert result == "hello world"
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_read_file_missing() -> None:
    tool = ReadFileTool()
    result = await tool.run(path="/tmp/nonexistent_openclawd_test_file.txt")
    assert "Error" in result


@pytest.mark.asyncio
async def test_write_file() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "sub", "out.txt")
        tool = WriteFileTool()
        result = await tool.run(path=path, content="data")
        assert "Successfully" in result
        assert os.path.isfile(path)
        with open(path) as f:
            assert f.read() == "data"


@pytest.mark.asyncio
async def test_list_directory() -> None:
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "a.txt"), "w").close()
        open(os.path.join(td, "b.txt"), "w").close()
        tool = ListDirectoryTool()
        result = await tool.run(path=td)
        assert "a.txt" in result
        assert "b.txt" in result
