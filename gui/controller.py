from database.sqlite_manager import SQLiteManager
from services.discovery_service import DiscoveryService


class AppController:
    def __init__(self):
        self.db = SQLiteManager()
        self.discovery_service = DiscoveryService()

    def get_dashboard_stats(self):
        jobs = self.db.get_all_jobs()

        total_jobs = len(jobs)
        new_jobs = len([job for job in jobs if job[14] == "NEW"]) if jobs else 0
        applied_jobs = len([job for job in jobs if job[15] == 1]) if jobs else 0

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

    def run_discovery(self):
        run = self.discovery_service.run_discovery()

        if run.errors:
            raise RuntimeError("; ".join(run.errors))

        return self.get_dashboard_stats()