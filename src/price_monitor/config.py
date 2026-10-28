from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centrais do projeto Price Monitor."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="PM_", extra="ignore"
    )

    # HTTP
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    timeout_seconds: float = 15.0
    max_retries: int = 3
    rate_limit_per_second: float = 2.0

    # Paths
    data_dir: str = "data"
    log_dir: str = "logs"
    log_level: str = "INFO"


settings = Settings()
