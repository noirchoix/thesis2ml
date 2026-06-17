from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Thesis2ML Chemistry"
    database_path: Path = Path("data/thesis2ml.db")
    storage_dir: Path = Path("data/uploads")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    generation_provider: str = "deepseek"
    fallback_generation_provider: str = "gemini"
    embedding_provider: str = "voyage"
    fallback_embedding_provider: str = "gemini"

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    gemini_api_key: str = ""
    gemini_generation_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "text-embedding-004"

    voyageai_api_key: str = ""
    voyage_embedding_model: str = "voyage-3-large"

    chunk_size: int = 1400
    chunk_overlap: int = 180
    top_k: int = 8
    max_context_chars: int = 14000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
