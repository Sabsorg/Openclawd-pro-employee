"""Workflow engine — multi-step workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow definition."""

    name: str
    handler: Callable[..., Awaitable[str]]
    args: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: str = ""


class Workflow:
    """A directed sequence of steps that forms a complete workflow.

    Steps can declare dependencies on other steps; the engine respects
    ordering while running them sequentially.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: dict[str, WorkflowStep] = {}

    def add_step(
        self,
        name: str,
        handler: Callable[..., Awaitable[str]],
        args: dict[str, Any] | None = None,
        depends_on: list[str] | None = None,
    ) -> None:
        """Register a step in the workflow."""
        self._steps[name] = WorkflowStep(
            name=name,
            handler=handler,
            args=args or {},
            depends_on=depends_on or [],
        )

    async def run(self) -> dict[str, str]:
        """Execute all steps in dependency order and return results keyed by step name."""
        completed: set[str] = set()
        results: dict[str, str] = {}

        while len(completed) < len(self._steps):
            progress = False
            for step_name, step in self._steps.items():
                if step_name in completed:
                    continue
                # Check deps.
                if not all(d in completed for d in step.depends_on):
                    continue

                step.status = StepStatus.RUNNING
                try:
                    step.result = await step.handler(**step.args)
                    step.status = StepStatus.COMPLETED
                except Exception as exc:  # noqa: BLE001
                    step.result = f"Error: {exc}"
                    step.status = StepStatus.FAILED

                results[step_name] = step.result
                completed.add(step_name)
                progress = True

            if not progress:
                # Remaining steps have unsatisfiable deps – mark skipped.
                for step_name, step in self._steps.items():
                    if step_name not in completed:
                        step.status = StepStatus.SKIPPED
                        results[step_name] = "Skipped (unmet dependencies)"
                        completed.add(step_name)

        return results

    @property
    def steps(self) -> list[WorkflowStep]:
        return list(self._steps.values())
