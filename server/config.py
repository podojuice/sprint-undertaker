from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8001
    database_url: str = "postgresql+asyncpg://rpg:rpg@db:5432/rpg"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    model_config = SettingsConfigDict(
        env_prefix="RPG_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
