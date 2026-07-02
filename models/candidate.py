from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Candidate:
    name: str

    candidate_profile: str = ""
    master_resume: dict = field(default_factory=dict)
    preferences: dict = field(default_factory=dict)
    technical_skills: dict = field(default_factory=dict)

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
