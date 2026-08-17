from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql+psycopg://repertoire:repertoire@localhost:5432/repertoire"
    sheet_resource_storage_dir: str = "/data/sheet-resources"
    sheet_resource_max_upload_bytes: int = 20 * 1024 * 1024


settings = Settings()
