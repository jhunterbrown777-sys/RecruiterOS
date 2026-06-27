from database.sqlite_manager import SQLiteManager
from services.google_jobs import GoogleJobsProvider
from services.manual_provider import ManualProvider


class DiscoveryPipeline:
    def __init__(self):
        self.db = SQLiteManager()
        self.providers = [
            ManualProvider(),
            GoogleJobsProvider(),
        ]

    def run(self):
        total_saved = 0

        queries = [
            "IT Support Specialist",
            "Service Desk Analyst",
            "SEO Specialist",
            "Google Ads Specialist",
        ]

        for provider in self.providers:
            for query in queries:
                jobs = provider.search_jobs(query=query, location="Remote")

                for job in jobs:
                    job_id = self.db.save_job(job)

                    if job_id:
                        total_saved += 1
                        print(f"Saved job #{job_id}: {job.title} at {job.company} from {job.source}")
                    else:
                        print(f"Skipped duplicate: {job.title} at {job.company} from {job.source}")

        print(f"Discovery complete. Saved {total_saved} new jobs.")