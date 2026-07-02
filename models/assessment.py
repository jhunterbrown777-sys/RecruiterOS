from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Assessment:
    opportunity_id: int

    score: int
    fit_score: int

    posting_age_score: int
    company_score: int
    remote_score: int
    salary_score: int
    ats_score: int

    recommendation: str
    reasoning: str

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
