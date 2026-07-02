from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

DOCUMENT_TYPES = [
    "Resume",
    "Cover Letter",
    "Certificate",
    "Portfolio",
    "Reference",
    "Attachment",
    "Other",
]


@dataclass
class Document:
    candidate_id: int
    title: str

    document_type: str = "Other"
    content: str = ""
    version: int = 1

    id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
