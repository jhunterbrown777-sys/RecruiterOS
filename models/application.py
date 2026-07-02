from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

APPLICATION_STATUSES = [
    "READY_TO_REVIEW",
    "APPLIED",
    "INTERVIEWING",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]


@dataclass
class Application:
    opportunity_id: int

    status: str = "READY_TO_REVIEW"

    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None

    notes: str = ""

    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
