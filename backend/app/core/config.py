from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://risklesson:risklesson@localhost:5432/risklesson"
    anthropic_api_key: str = ""


settings = Settings()
