from database.sqlite_manager import SQLiteManager
from models.job import Job
from models.opportunity import Opportunity


class OpportunityService:
    """Service-layer interface for Opportunity data.

    Wraps SQLiteManager's opportunity persistence methods so callers
    depend on the service layer instead of the persistence layer
    directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_opportunity(self, opportunity: Opportunity) -> int | None:
        """Persist a new Opportunity and return its id, or None if a
        matching (candidate_id, job_id) pair already exists."""
        return self.db.save_opportunity(opportunity)

    def get_opportunity(self, opportunity_id: int) -> Opportunity | None:
        """Fetch an Opportunity by id, or None if not found."""
        return self.db.get_opportunity(opportunity_id)

    def list_opportunities(self, candidate_id: int) -> list[Opportunity]:
        """List all Opportunities belonging to a Candidate."""
        return self.db.get_opportunities(candidate_id)

    def update_opportunity(self, opportunity: Opportunity) -> None:
        """Persist changes to an existing Opportunity."""
        self.db.update_opportunity(opportunity)

    def list_opportunities_with_jobs(self, candidate_id: int) -> list[tuple[Opportunity, Job | None]]:
        """List a Candidate's Opportunities paired with their Job."""
        opportunities = self.db.get_opportunities(candidate_id)

        return [
            (opportunity, self.db.get_job(opportunity.job_id))
            for opportunity in opportunities
        ]
