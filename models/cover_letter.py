from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CoverLetter:
    candidate_id: int
    title: str

    content: str = ""
    version: int = 1

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
