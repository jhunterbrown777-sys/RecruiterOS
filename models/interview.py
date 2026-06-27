from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Interview:
    job_id: int
    company: str
    role: str

    stage: str = "SCREENING"
    interview_date: Optional[datetime] = None

    interviewer_names: str = ""
    interview_format: str = ""
    notes: str = ""
    technical_questions: str = ""
    behavioral_questions: str = ""
    outcome: str = ""

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)