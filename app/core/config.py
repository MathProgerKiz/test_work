from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения с переменными окружения"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    ### Celery
    celery_broker_url: str = Field(
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        validation_alias="CELERY_RESULT_BACKEND",
    )
    ### Database
    database_url: str = Field(
        validation_alias="DATABASE_URL",
        description="URL подключения к PostgreSQL",
    )


settings = Settings()
