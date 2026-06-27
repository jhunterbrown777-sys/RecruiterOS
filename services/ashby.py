from typing import List

from models.job import Job
from services.base_provider import BaseJobProvider


class AshbyProvider(BaseJobProvider):
    provider_name = "Ashby"

    def search_jobs(self, query: str, location: str = "Remote") -> List[Job]:
        return [
            Job(
                title=query,
                company="Ashby Demo Company",
                location=location,
                description=f"Demo Ashby result for query: {query}",
                url=f"https://example.com/ashby/{query.lower().replace(' ', '-')}",
                source=self.provider_name,
                work_arrangement=location,
                employment_type="Full-time",
                remote=location.lower() == "remote",
                ats_platform="Ashby",
            )
        ]