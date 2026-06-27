from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    profile_dir: str

    candidate_profile: str
    master_resume: dict
    preferences: dict
    technical_skills: dict