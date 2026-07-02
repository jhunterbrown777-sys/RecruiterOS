from database.sqlite_manager import SQLiteManager
from models.resume import Resume


class ResumeService:
    """Service-layer interface for Resume data.

    Wraps SQLiteManager's resume persistence methods so callers depend
    on the service layer instead of the persistence layer directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_resume(self, resume: Resume) -> int:
        """Persist a new Resume and return its id."""
        return self.db.save_resume(resume)

    def get_resume(self, resume_id: int) -> Resume | None:
        """Fetch a Resume by id, or None if not found."""
        return self.db.get_resume(resume_id)

    def list_resumes(self, candidate_id: int) -> list[Resume]:
        """List all Resumes belonging to a Candidate, most recently updated first."""
        return self.db.get_resumes(candidate_id)

    def update_resume(self, resume: Resume) -> None:
        """Persist changes to an existing Resume."""
        self.db.update_resume(resume)
