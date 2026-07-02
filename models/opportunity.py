from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Opportunity:
    candidate_id: int
    job_id: int

    status: str = "SCOUTED"

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
