from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from orchestrator.state import WorkflowState


@dataclass
class WorkflowRun:
    profile_name: str
    state: WorkflowState = WorkflowState.CREATED

    current_step: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_state(self, state: WorkflowState, step: str = "") -> None:
        self.state = state
        self.current_step = step
        self.updated_at = datetime.utcnow()

    def add_result(self, key: str, value: Any) -> None:
        self.result[key] = value
        self.updated_at = datetime.utcnow()

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.state = WorkflowState.FAILED
        self.updated_at = datetime.utcnow()