from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='./.env', extra="ignore")
    # pg: postgresql+psycopg://user:secret@localhost:5432/db
    DATABASE_URL: str = "sqlite:///sqlite.db"


settings = Settings()

if __name__ == "__main__":
    print(Settings().model_dump())