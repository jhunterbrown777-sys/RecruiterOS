from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Application:
    job_id: int
    company_id: int

    status: str = "READY_TO_REVIEW"

    resume_path: str = ""
    cover_letter_path: str = ""
    recruiter_message_path: str = ""
    ats_report_path: str = ""

    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)