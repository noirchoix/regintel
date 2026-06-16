from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = Field(default='Regulatory Intelligence Engine API')
    app_env: str = Field(default='development')
    app_debug: bool = Field(default=False)
    api_prefix: str = Field(default='/v1')
    secret_key: str = Field(default='change-me-in-production')
    access_token_expire_minutes: int = Field(default=720)
    bootstrap_admin_email: str = Field(default='admin@regintel.local')
    bootstrap_admin_password: str = Field(default='Admin123!')

    database_url: str = Field(default='postgresql+psycopg://postgres:postgres@localhost:5432/regintel')
    redis_url: str = Field(default='redis://localhost:6379/0')

    qdrant_url: str = Field(default='http://localhost:6333')
    qdrant_api_key: str | None = None
    qdrant_collection: str = Field(default='regulatory_documents')
    qdrant_vector_size: int = Field(default=1024)

    voyage_api_key: str | None = None
    voyage_embedding_model: str = Field(default='voyage-3-large')

    deepseek_api_key: str | None = None
    deepseek_base_url: str = Field(default='https://api.deepseek.com')
    deepseek_model: str = Field(default='deepseek-chat')

    pdf_worker_url: str = Field(default='http://localhost:8010')

    uploads_dir: str = Field(default='./data/uploads')
    artifacts_dir: str = Field(default='./data/artifacts')

    cors_origins: str = Field(default='http://localhost:5173,http://127.0.0.1:5173')
    sentry_dsn: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]

    @property
    def uploads_path(self) -> Path:
        path = (BASE_DIR / self.uploads_dir).resolve() if not Path(self.uploads_dir).is_absolute() else Path(self.uploads_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def artifacts_path(self) -> Path:
        path = (BASE_DIR / self.artifacts_dir).resolve() if not Path(self.artifacts_dir).is_absolute() else Path(self.artifacts_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()