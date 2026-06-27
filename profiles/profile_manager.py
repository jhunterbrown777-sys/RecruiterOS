import json
import os
from pathlib import Path

from profiles.profile import Profile


class ProfileManager:
    def __init__(self, profiles_root: str = "private_memory"):
        self.profiles_root = Path(profiles_root)

    def load(self, profile_name: str | None = None) -> Profile:
        active_profile = profile_name or os.getenv("ACTIVE_PROFILE", "hunter")
        profile_dir = self.profiles_root / active_profile

        if not profile_dir.exists():
            raise FileNotFoundError(f"Profile directory not found: {profile_dir}")

        return Profile(
            name=active_profile,
            profile_dir=str(profile_dir),
            candidate_profile=self._read_text(profile_dir / "candidate_profile.md"),
            master_resume=self._read_json(profile_dir / "master_resume.json"),
            preferences=self._read_json(profile_dir / "preferences.json"),
            technical_skills=self._read_json(profile_dir / "technical_skills.json"),
        )

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"Missing profile file: {path}")

        return path.read_text(encoding="utf-8")

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Missing profile file: {path}")

        return json.loads(path.read_text(encoding="utf-8"))