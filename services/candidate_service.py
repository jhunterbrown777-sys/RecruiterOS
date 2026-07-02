from database.sqlite_manager import SQLiteManager
from models.candidate import Candidate


class CandidateService:
    """Service-layer interface for Candidate data.

    Wraps SQLiteManager's candidate persistence methods so callers depend
    on the service layer instead of the persistence layer directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def save_candidate(self, candidate: Candidate) -> int:
        """Persist a new Candidate and return its id."""
        return self.db.save_candidate(candidate)

    def get_candidate(self, candidate_id: int) -> Candidate | None:
        """Fetch a Candidate by id, or None if not found."""
        return self.db.get_candidate(candidate_id)

    def update_candidate(self, candidate: Candidate) -> None:
        """Persist changes to an existing Candidate."""
        self.db.update_candidate(candidate)
