from database.sqlite_manager import SQLiteManager
from models.application import Application


class ApplicationService:
    """Service-layer interface for Application data.

    Wraps SQLiteManager's application persistence methods so callers
    depend on the service layer instead of the persistence layer
    directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_application(self, application: Application) -> int | None:
        """Persist a new Application and return its id, or None if a
        matching opportunity_id already has one (0..1 per the ERD)."""
        return self.db.save_application(application)

    def get_application(self, application_id: int) -> Application | None:
        """Fetch an Application by id, or None if not found."""
        return self.db.get_application(application_id)

    def get_application_by_opportunity(self, opportunity_id: int) -> Application | None:
        """Fetch the Application for a given Opportunity, or None if there isn't one."""
        return self.db.get_application_by_opportunity(opportunity_id)

    def list_applications(self) -> list[Application]:
        """List all Applications, most recently updated first."""
        return self.db.get_applications()

    def update_application(self, application: Application) -> None:
        """Persist changes to an existing Application."""
        self.db.update_application(application)
