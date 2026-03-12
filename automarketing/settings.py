from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTOMARKETING_", extra="ignore")

    app_name: str = "Automarketing Control Plane"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

