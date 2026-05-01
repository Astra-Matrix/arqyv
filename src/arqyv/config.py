"""Central application configuration using Pydantic Settings.

Values are resolved in order: defaults → config file → env vars → CLI overrides.
"""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir, user_config_dir, user_cache_dir
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_APP_NAME = "ARQYV"
_APP_AUTHOR = "Alaustrup"


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARQYV_DB_")

    url: str = Field(default="", description="SQLAlchemy database URL. Auto-set if empty.")
    echo: bool = Field(default=False, description="Log all SQL statements (debug).")
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)


class AIConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARQYV_AI_")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace model used for semantic embeddings.",
    )
    whisper_model: str = Field(
        default="base",
        description="Whisper model size: tiny | base | small | medium | large.",
    )
    device: str = Field(default="auto", description="Torch device: auto | cpu | cuda | mps.")
    batch_size: int = Field(default=16)
    max_workers: int = Field(default=4, description="Thread-pool size for AI inference.")


class CloudConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARQYV_CLOUD_")

    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    onedrive_client_id: str = Field(default="")
    dropbox_app_key: str = Field(default="")
    dropbox_app_secret: str = Field(default="")


class MediaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARQYV_MEDIA_")

    thumbnail_size: tuple[int, int] = Field(default=(320, 240))
    thumbnail_quality: int = Field(default=85, ge=1, le=100)
    supported_video: list[str] = Field(
        default=[
            ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
            ".m4v", ".3gp", ".ogv", ".ts", ".mts", ".m2ts",
        ]
    )
    supported_audio: list[str] = Field(
        default=[
            ".mp3", ".flac", ".wav", ".aac", ".ogg", ".opus",
            ".m4a", ".wma", ".aiff", ".ape", ".mka",
        ]
    )
    supported_image: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg", ".heic"]
    )
    supported_document: list[str] = Field(
        default=[".pdf", ".docx", ".doc", ".txt", ".md", ".xlsx", ".pptx", ".epub"]
    )


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ARQYV_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Directories ────────────────────────────────────────────────────────
    data_dir: Path = Field(default_factory=lambda: Path(user_data_dir(_APP_NAME, _APP_AUTHOR)))
    config_dir: Path = Field(default_factory=lambda: Path(user_config_dir(_APP_NAME, _APP_AUTHOR)))
    cache_dir: Path = Field(default_factory=lambda: Path(user_cache_dir(_APP_NAME, _APP_AUTHOR)))

    # ── UI ─────────────────────────────────────────────────────────────────
    theme: str = Field(default="dark", description="UI theme: dark | light.")
    language: str = Field(default="en")
    window_width: int = Field(default=1440)
    window_height: int = Field(default=900)
    sidebar_width: int = Field(default=260)

    # ── Feature flags ──────────────────────────────────────────────────────
    enable_ai: bool = Field(default=True)
    enable_voice_search: bool = Field(default=True)
    enable_cloud_sync: bool = Field(default=False)
    enable_auto_index: bool = Field(default=True)
    enable_api_server: bool = Field(default=True, description="Start the local REST/WebSocket API at localhost:8765.")

    # ── API server ─────────────────────────────────────────────────────────
    api_port: int = Field(default=8765, description="Port for the local API server.")

    # ── Microservice overrides (Version B / Docker) ────────────────────────────
    # Set DATABASE_URL / REDIS_URL in docker-compose environment; they take
    # precedence over the sqlite defaults used in monolith mode.
    database_url: str = Field(
        default="",
        description="Full SQLAlchemy URL (Docker). Overrides db.url and sqlite default.",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Version B event bus.",
    )

    # ── Sub-configs ────────────────────────────────────────────────────────
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    cloud: CloudConfig = Field(default_factory=CloudConfig)
    media: MediaConfig = Field(default_factory=MediaConfig)

    @field_validator("data_dir", "config_dir", "cache_dir", mode="after")
    @classmethod
    def _ensure_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def db_url(self) -> str:
        # Priority: DATABASE_URL env var (Docker) → db.url → SQLite default
        if self.database_url:
            return self.database_url
        if self.db.url:
            return self.db.url
        return f"sqlite+aiosqlite:///{self.data_dir / 'arqyv.db'}"

    @property
    def vector_db_path(self) -> Path:
        p = self.data_dir / "vectordb"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def thumbnail_cache_path(self) -> Path:
        p = self.cache_dir / "thumbnails"
        p.mkdir(parents=True, exist_ok=True)
        return p


# Global singleton — import and use anywhere in the monolith.
config = AppConfig()


def settings_from_env() -> AppConfig:
    """
    Create a fresh AppConfig fully hydrated from environment variables.

    Used by Version B microservice workers so each Docker container reads
    its own DATABASE_URL, REDIS_URL, and ARQYV_* env vars independently.
    """
    return AppConfig()
