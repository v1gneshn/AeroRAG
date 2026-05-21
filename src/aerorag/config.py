"""Centralized configuration loaded from environment / .env."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    chat_model: str = Field("gpt-4o-mini", alias="AERORAG_CHAT_MODEL")
    embed_model: str = Field("text-embedding-3-small", alias="AERORAG_EMBED_MODEL")

    data_dir: Path = Field(Path("./data"), alias="AERORAG_DATA_DIR")
    chroma_dir: Path = Field(Path("./data/processed/chroma"), alias="AERORAG_CHROMA_DIR")

    top_k: int = Field(5, alias="AERORAG_TOP_K")
    rerank_top_k: int = Field(25, alias="AERORAG_RERANK_TOP_K")
    rerank_model: str = Field(
        "cross-encoder/ms-marco-MiniLM-L-6-v2", alias="AERORAG_RERANK_MODEL"
    )

    log_level: str = Field("INFO", alias="AERORAG_LOG_LEVEL")

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def interim_dir(self) -> Path:
        return self.data_dir / "interim"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"


settings = Settings()
