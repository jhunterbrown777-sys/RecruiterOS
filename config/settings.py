from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path = Path("database/recruiteros.db")
    output_dir: Path = Path("data/outputs")
    logs_dir: Path = Path("logs")
    private_memory_dir: Path = Path("private_memory")
    default_profile: str = "hunter"
    minimum_fit_score: int = 75
    ats_regeneration_threshold: int = 85


settings = Settings()