from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # All values are read from .env; missing required fields raise a startup error
    model_config = SettingsConfigDict(env_file=".env")

    devin_api_token: str
    devin_api_base_url: str = "https://api.devin.ai/v1"

    github_token: str
    github_webhook_secret: str
    github_repo: str  # format: "owner/repo"

    database_url: str = "sqlite:///./data/tasks.db"

    poll_interval_seconds: int = 30
    remediation_label: str = "automation:remediation"


# Module-level singleton — imported directly by all other modules
settings = Settings()
