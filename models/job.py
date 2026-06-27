from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:

    title: str
    company: str
    location: str

    description: str = ""

    url: str = ""

    source: str = ""

    work_arrangement: str = ""

    employment_type: str = ""

    salary: Optional[str] = None

    recruiter: Optional[str] = None

    date_posted: Optional[str] = None

    discovered_at: datetime = field(default_factory=datetime.utcnow)

    fit_score: Optional[int] = None

    status: str = "NEW"

    applied: bool = False

    notes: str = ""

    company_size: str = ""

    industry: str = ""

    ats_platform: str = ""

    remote: bool = False