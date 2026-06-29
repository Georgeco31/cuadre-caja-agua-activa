from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Cuadre de Caja Agua Activa"
    api_service_name: str = "cuadre-caja-api"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://cuadre_user:cuadre_password@localhost:5432/"
        "cuadre_caja"
    )
    admin_username: str = "admin"
    admin_password: str | None = None
    admin_is_active: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
