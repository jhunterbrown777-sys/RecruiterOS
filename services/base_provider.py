from abc import ABC, abstractmethod
from typing import List

from models.job import Job


class BaseJobProvider(ABC):
    provider_name: str = "Base Provider"

    @abstractmethod
    def search_jobs(self, query: str, location: str = "Remote") -> List[Job]:
        pass