from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Recruiter:
    name: str
    company: str

    title: str = ""
    linkedin_url: str = ""
    email: str = ""
    phone: str = ""

    source: str = ""
    notes: str = ""

    last_contacted_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)