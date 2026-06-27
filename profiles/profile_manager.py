import json
from pathlib import Path

from config.settings import settings
from profiles.profile import Profile


class ProfileManager:
    def __init__(self):
        self.root = settings.private_memory_dir

    def available_profiles(self):
        if not self.root.exists():
            return []

        return sorted(
            [
                folder.name
                for folder in self.root.iterdir()
                if folder.is_dir()
            ]
        )

    def load(self, profile_name=None):

        profile_name = profile_name or settings.default_profile

        profile_dir = self.root / profile_name

        if not profile_dir.exists():
            raise FileNotFoundError(
                f"Profile '{profile_name}' not found.\n"
                f"Available profiles: {self.available_profiles()}"
            )

        return Profile(
            name=profile_name,
            profile_dir=str(profile_dir),
            candidate_profile=self._text(profile_dir / "candidate_profile.md"),
            master_resume=self._json(profile_dir / "master_resume.json"),
            preferences=self._json(profile_dir / "preferences.json"),
            technical_skills=self._json(profile_dir / "technical_skills.json"),
        )

    def _text(self, path):
        return path.read_text(encoding="utf-8")

    def _json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))