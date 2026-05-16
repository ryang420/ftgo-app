from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    service_name: str
    environment: str = "local"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="FTGO_",
        env_file=".env",
        extra="ignore",
    )
