from typing import List

from models.job import Job
from services.base_provider import BaseJobProvider


class GoogleJobsProvider(BaseJobProvider):
    provider_name = "Google Jobs"

    def search_jobs(self, query: str, location: str = "Remote") -> List[Job]:
        """
        Placeholder Google Jobs provider.

        Future implementation:
        - Search Google Jobs or a supported jobs API
        - Normalize results into Job objects
        - Return List[Job]
        """

        return [
            Job(
                title=query,
                company="Google Jobs Demo Company",
                location=location,
                description=f"""
Demo result from Google Jobs for query: {query}

This placeholder simulates a normalized Google Jobs result.
Future versions will replace this with real job discovery.
""",
                url=f"https://example.com/google-jobs/{query.lower().replace(' ', '-')}",
                source=self.provider_name,
                work_arrangement=location,
                employment_type="Full-time",
                salary="",
                remote=location.lower() == "remote",
            )
        ]