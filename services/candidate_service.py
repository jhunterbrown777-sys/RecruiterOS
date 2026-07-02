from config.settings import settings
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

    def get_or_create_candidate(self, default_name: str) -> Candidate:
        """Fetch the current Candidate, creating one with default_name if none exists."""
        candidate = self.db.get_first_candidate()

        if candidate is not None:
            return candidate

        candidate_id = self.db.save_candidate(Candidate(name=default_name))
        return self.db.get_candidate(candidate_id)

    def get_default_candidate(self) -> Candidate:
        """Fetch (or create) the single default Candidate."""
        return self.get_or_create_candidate(settings.default_profile)
