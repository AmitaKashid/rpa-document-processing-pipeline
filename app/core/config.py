from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RPA Document Validation Pipeline"
    database_url: str = "sqlite:///./audit.db"
    output_dir: Path = Path("data/output")
    min_confidence_for_automation: float = 0.88

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
settings.output_dir.mkdir(parents=True, exist_ok=True)
