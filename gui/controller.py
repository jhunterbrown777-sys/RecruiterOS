from database.sqlite_manager import SQLiteManager
from pipelines.discovery_pipeline import DiscoveryPipeline


class AppController:
    def __init__(self):
        self.db = SQLiteManager()

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
        }

    def get_recent_jobs(self, limit=5):
        jobs = self.db.get_all_jobs()
        return jobs[:limit]

    def run_discovery(self):
        pipeline = DiscoveryPipeline()
        pipeline.run()
        return self.get_dashboard_stats()