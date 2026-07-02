from database.sqlite_manager import SQLiteManager
from models.assessment import Assessment


class AssessmentService:
    """Service-layer interface for Assessment data.

    Wraps SQLiteManager's assessment persistence methods so callers
    depend on the service layer instead of the persistence layer
    directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_assessment(self, assessment: Assessment) -> int:
        """Persist a new Assessment and return its id."""
        return self.db.save_assessment(assessment)

    def get_assessment(self, assessment_id: int) -> Assessment | None:
        """Fetch an Assessment by id, or None if not found."""
        return self.db.get_assessment(assessment_id)

    def list_assessments(self, opportunity_id: int) -> list[Assessment]:
        """List all Assessments for a given Opportunity, most recent first."""
        return self.db.get_assessments(opportunity_id)
