from config.settings import settings
from database.sqlite_manager import SQLiteManager
from models.candidate import Candidate
from services.candidate_service import CandidateService
from services.discovery_service import DiscoveryService
from services.opportunity_service import OpportunityService


class AppController:
    def __init__(self):
        self.db = SQLiteManager()
        self.discovery_service = DiscoveryService()
        self.candidate_service = CandidateService()
        self.opportunity_service = OpportunityService()

    def get_dashboard_stats(self):
        jobs = self.db.get_all_jobs()

        total_jobs = len(jobs)
        new_jobs = len([job for job in jobs if job.status == "NEW"]) if jobs else 0
        applied_jobs = len([job for job in jobs if job.applied]) if jobs else 0

        return {
            "jobs_discovered": total_jobs,
            "qualified_opportunities": new_jobs,
            "applications_sent": applied_jobs,
            "interviews": 0,
            "offers": 0,
            "ready_queue": new_jobs,
            "average_ats": 92,
        }

    def get_recent_jobs(self, limit=8):
        jobs = self.db.get_all_jobs()
        return jobs[:limit]

    def get_top_opportunities(self, limit=5):
        jobs = self.db.get_all_jobs()
        return jobs[:limit]

    def get_activity_feed(self):
        return [
            "Google Jobs provider checked",
            "Greenhouse provider checked",
            "Lever provider checked",
            "Discovery pipeline completed",
            "Waiting for application review",
        ]

    def get_mission_items(self):
        return [
            ("Discover Jobs", True),
            ("Score Opportunities", True),
            ("Company Research", False),
            ("Resume Optimization", False),
            ("Browser Automation", False),
        ]

    def get_candidate(self) -> Candidate:
        return self.candidate_service.get_or_create_candidate(settings.default_profile)

    def update_candidate(self, name: str, candidate_profile: str) -> None:
        candidate = self.get_candidate()
        candidate.name = name
        candidate.candidate_profile = candidate_profile
        self.candidate_service.update_candidate(candidate)

    def get_opportunities(self):
        candidate = self.get_candidate()
        return self.opportunity_service.list_opportunities_with_jobs(candidate.id)

    def run_discovery(self):
        run = self.discovery_service.run_discovery()

        if run.errors:
            raise RuntimeError("; ".join(run.errors))

        return self.get_dashboard_stats()