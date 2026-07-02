from dataclasses import dataclass

from models.candidate import Candidate
from services.candidate_service import CandidateService


@dataclass
class RecruiterContext:
    """Input context passed to recruiting agent factories.

    Currently carries only the active Candidate. Designed to grow to
    include Opportunities, Assessments, Documents, Companies, Contacts,
    and notes as agents need them -- add fields here as those needs
    arise, not speculatively ahead of time.
    """

    candidate: Candidate


class RecruiterContextBuilder:
    """Builds a RecruiterContext from persisted data via services."""

    def __init__(self):
        self.candidate_service = CandidateService()

    def build_default(self) -> RecruiterContext:
        """Build a RecruiterContext for the default (single) Candidate."""
        candidate = self.candidate_service.get_default_candidate()
        return RecruiterContext(candidate=candidate)
