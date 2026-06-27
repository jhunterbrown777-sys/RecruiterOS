from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class QueueItem:
    task_type: str
    payload: dict[str, Any]

    priority: int = 5
    status: str = "PENDING"

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempts: int = 0
    max_attempts: int = 3

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_running(self) -> None:
        self.status = "RUNNING"
        self.attempts += 1
        self.updated_at = datetime.utcnow()

    def mark_complete(self) -> None:
        self.status = "COMPLETE"
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        self.status = "FAILED"
        self.updated_at = datetime.utcnow()


class WorkflowQueue:
    def __init__(self):
        self.items: list[QueueItem] = []

    def add(self, item: QueueItem) -> None:
        self.items.append(item)
        self.items.sort(key=lambda x: x.priority)

    def next_item(self) -> QueueItem | None:
        for item in self.items:
            if item.status == "PENDING":
                return item
        return None

    def pending_count(self) -> int:
        return len([item for item in self.items if item.status == "PENDING"])