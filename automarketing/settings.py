from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTOMARKETING_", extra="ignore")

    app_name: str = "Automarketing Control Plane"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    database_url: str = "sqlite+pysqlite:///./automarketing.db"
    database_schema: str = "automarketing"
    database_echo: bool = False
    seed_demo_data: bool = True
    bootstrap_schema: bool = False
    official_registry_url: str = "https://registry.modelcontextprotocol.io/v0.1/servers"
    serpapi_base_url: str = "https://serpapi.com/search"
    serpapi_api_key: str | None = None
    google_search_console_base_url: str = (
        "https://www.googleapis.com/webmasters/v3"
    )
    google_api_access_token: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
