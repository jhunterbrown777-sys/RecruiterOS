from typing import List

from models.job import Job
from services.base_provider import BaseJobProvider


class LeverProvider(BaseJobProvider):
    provider_name = "Lever"

    def search_jobs(self, query: str, location: str = "Remote") -> List[Job]:
        return [
            Job(
                title=query,
                company="Lever Demo Company",
                location=location,
                description=f"Demo Lever result for query: {query}",
                url=f"https://example.com/lever/{query.lower().replace(' ', '-')}",
                source=self.provider_name,
                work_arrangement=location,
                employment_type="Full-time",
                remote=location.lower() == "remote",
                ats_platform="Lever",
            )
        ]