from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class CelerySettings(AppSettings):
    celery_broker_url: str = Field(
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        validation_alias="CELERY_RESULT_BACKEND",
    )


class DatabaseSettings(AppSettings):
    database_url: str = Field(
        validation_alias="DATABASE_URL",
        description="URL подключения к PostgreSQL",
    )
