import json
import os
from pathlib import Path


class MemoryManager:
    def __init__(self, memory_root: str = "private_memory"):
        active_profile = os.getenv("ACTIVE_PROFILE", "hunter")
        self.profile_dir = Path(memory_root) / active_profile

    def _read_text(self, filename: str) -> str:
        path = self.profile_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing private memory file: {path}")

        return path.read_text(encoding="utf-8")

    def _read_json(self, filename: str) -> dict:
        path = self.profile_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing private memory file: {path}")

        return json.loads(path.read_text(encoding="utf-8"))

    def candidate_profile(self) -> str:
        return self._read_text("candidate_profile.md")

    def master_resume(self) -> dict:
        return self._read_json("master_resume.json")

    def preferences(self) -> dict:
        return self._read_json("preferences.json")

    def technical_skills(self) -> dict:
        return self._read_json("technical_skills.json")