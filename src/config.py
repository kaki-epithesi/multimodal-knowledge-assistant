from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Lightweight config using Pydantic v2-style settings.
class Settings(BaseSettings):
    app_name: str = Field(default="multimodal-knowledge-assistant", alias="APP_NAME")
    app_version: str = Field(default="0.1", alias="APP_VERSION")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
