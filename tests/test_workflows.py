"""Tests for the workflow engine."""

from __future__ import annotations

import pytest

from openclawd_employee.workflows import Workflow, StepStatus


async def _greet(name: str = "world") -> str:
    return f"Hello, {name}!"


async def _upper(text: str = "") -> str:
    return text.upper()


async def _fail() -> str:
    raise RuntimeError("intentional failure")


@pytest.mark.asyncio
async def test_simple_workflow() -> None:
    wf = Workflow("test")
    wf.add_step("greet", _greet, args={"name": "Agent"})
    results = await wf.run()
    assert results["greet"] == "Hello, Agent!"
    assert wf.steps[0].status == StepStatus.COMPLETED


@pytest.mark.asyncio
async def test_workflow_dependency_order() -> None:
    wf = Workflow("test")
    wf.add_step("greet", _greet, args={"name": "Agent"})
    wf.add_step("upper", _upper, args={"text": "done"}, depends_on=["greet"])
    results = await wf.run()
    assert results["upper"] == "DONE"


@pytest.mark.asyncio
async def test_workflow_failure_handling() -> None:
    wf = Workflow("test")
    wf.add_step("fail", _fail)
    results = await wf.run()
    assert "Error" in results["fail"]
    assert wf.steps[0].status == StepStatus.FAILED


@pytest.mark.asyncio
async def test_workflow_skipped_on_unmet_deps() -> None:
    wf = Workflow("test")
    wf.add_step("step_a", _greet, depends_on=["missing_step"])
    results = await wf.run()
    assert wf.steps[0].status == StepStatus.SKIPPED
