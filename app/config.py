from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    devin_api_token: str
    devin_api_base_url: str = "https://api.devin.ai/v1"

    github_token: str
    github_webhook_secret: str
    github_repo: str  # e.g. "patelajk/superset"

    database_url: str = "sqlite:///./data/tasks.db"

    poll_interval_seconds: int = 30
    remediation_label: str = "automation:remediation"


settings = Settings()
