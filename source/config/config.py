from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TG_BOT_",
    )
    db: str
    key: str


settings = Settings()  # type: ignore
print(settings.db)