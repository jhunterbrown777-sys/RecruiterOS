from config.settings import settings
from orchestrator.chief_recruiter import ChiefRecruiter
from orchestrator.workflow import WorkflowRun


class DiscoveryService:
    """GUI/CLI-facing entry point for running job discovery.

    Wraps ChiefRecruiter.run_discovery_workflow() so callers depend on the
    service layer instead of the orchestrator or pipeline layers directly.
    """

    def __init__(self, profile_name: str | None = None):
        self.profile_name = profile_name or settings.default_profile

    def run_discovery(self) -> WorkflowRun:
        """Run the discovery workflow and return its WorkflowRun result."""
        chief = ChiefRecruiter(profile_name=self.profile_name)
        return chief.run_discovery_workflow()
