from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8001
    db_user: str = "rpg"
    db_password: str = "rpg"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "rpg"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@sprint-undertaker.local"
    smtp_tls: bool = True
    plugin_version_latest: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_prefix="RPG_",
        env_file=".env",
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
