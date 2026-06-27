from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    name: str

    website: str = ""
    linkedin_url: str = ""
    careers_url: str = ""

    industry: str = ""
    company_size: str = ""
    headquarters: str = ""

    glassdoor_rating: Optional[float] = None

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)