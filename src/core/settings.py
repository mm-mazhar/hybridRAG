from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Self

import yaml
from pydantic import AliasChoices, BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.paths import project_root, resolve_under_root


class LlmConfig(BaseModel):
    """Chat-completion provider settings (OpenAI-compatible)."""

    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 8191
    models: list[str] = Field(default_factory=list)

    @field_validator("base_url")
    @classmethod
    def strip_base_url(cls, value: str) -> str:
        return value.rstrip("/")


class EmbeddingsConfig(BaseModel):
    """Embedding provider settings (OpenAI-compatible)."""

    base_url: str
    model: str
    batch_size: int = 64

    @field_validator("base_url")
    @classmethod
    def strip_base_url(cls, value: str) -> str:
        return value.rstrip("/")


class VectorDbConfig(BaseModel):
    """LanceDB location and retrieval defaults."""

    uri: str = "data/vectordb"
    mode: str = "overwrite"
    limit: int = 8
    hybrid: bool = True
    multi_query: bool = True


class MemoryConfig(BaseModel):
    """SQLite chat-memory location."""

    path: str = "data/cache/memory.sqlite"


class AppMetaConfig(BaseModel):
    """Non-secret app metadata used for headers and CORS."""

    title: str = "hybridRAG"
    http_referer: str = "http://localhost:3000"
    frontend_origin: str = "http://localhost:3000"
    max_upload_bytes: int = 25 * 1024 * 1024


class IngestConfig(BaseModel):
    """URL table-name helpers."""

    common_tlds: list[str] = Field(default_factory=list)


class ModelFileConfig(BaseModel):
    """Shape of `config/model_config.yaml`."""

    llm: LlmConfig
    embeddings: EmbeddingsConfig
    vector_db: VectorDbConfig = Field(default_factory=VectorDbConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    app: AppMetaConfig = Field(default_factory=AppMetaConfig)
    ingest: IngestConfig = Field(default_factory=IngestConfig)


class EnvSettings(BaseSettings):
    """Secrets and path overrides from the environment."""

    llm_api_key: str = Field(validation_alias=AliasChoices("LLM_API_KEY", "OPENAI_API_KEY"))
    vector_db_uri: str | None = Field(default=None, validation_alias="VECTOR_DB_URI")
    memory_db_path: str | None = Field(default=None, validation_alias="MEMORY_DB_PATH")
    frontend_origin: str | None = Field(default=None, validation_alias="FRONTEND_ORIGIN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def provider_key_mismatch(api_key: str, *base_urls: str) -> str | None:
    """Return an error if an OpenRouter URL is paired with a non-OpenRouter key."""
    uses_openrouter = any("openrouter.ai" in url for url in base_urls)
    if uses_openrouter and not api_key.startswith("sk-or-"):
        return (
            "config points at OpenRouter but the API key is not an OpenRouter key "
            "(sk-or-...). Set llm.base_url and embeddings.base_url to "
            "https://api.openai.com/v1, or set LLM_API_KEY to an OpenRouter key."
        )
    return None


class AppSettings(BaseModel):
    """Merged YAML + environment configuration."""

    llm_api_key: str
    llm: LlmConfig
    embeddings: EmbeddingsConfig
    vector_db: VectorDbConfig
    memory: MemoryConfig
    app: AppMetaConfig
    ingest: IngestConfig
    vector_db_path: Path
    memory_db_path: Path

    @classmethod
    def load(cls, config_path: Path | None = None) -> Self:
        """Load YAML, overlay env, and fail fast if the API key is missing."""
        yaml_path = config_path or project_root() / "config" / "model_config.yaml"
        if not yaml_path.is_file():
            raise FileNotFoundError(f"Model config not found: {yaml_path}")

        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        file_cfg = ModelFileConfig.model_validate(raw)
        env = EnvSettings()
        mismatch = provider_key_mismatch(
            env.llm_api_key,
            file_cfg.llm.base_url,
            file_cfg.embeddings.base_url,
        )
        if mismatch:
            raise ValueError(mismatch)

        models = file_cfg.llm.models or [file_cfg.llm.model]
        if file_cfg.llm.model not in models:
            models = [file_cfg.llm.model, *models]
        llm = file_cfg.llm.model_copy(update={"models": models})

        app_meta = file_cfg.app
        if env.frontend_origin:
            app_meta = app_meta.model_copy(update={"frontend_origin": env.frontend_origin})

        vector_uri = env.vector_db_uri or file_cfg.vector_db.uri
        memory_path = env.memory_db_path or file_cfg.memory.path
        vector_db_path = resolve_under_root(vector_uri)
        memory_db_path = resolve_under_root(memory_path)
        vector_db_path.mkdir(parents=True, exist_ok=True)
        memory_db_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(
            llm_api_key=env.llm_api_key,
            llm=llm,
            embeddings=file_cfg.embeddings,
            vector_db=file_cfg.vector_db.model_copy(update={"uri": str(vector_db_path)}),
            memory=file_cfg.memory.model_copy(update={"path": str(memory_db_path)}),
            app=app_meta,
            ingest=file_cfg.ingest,
            vector_db_path=vector_db_path,
            memory_db_path=memory_db_path,
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return process-wide settings. Crashes on missing required env."""
    try:
        return AppSettings.load()
    except ValidationError as exc:
        print("CONFIGURATION ERROR", file=sys.stderr)
        print(exc, file=sys.stderr)
        raise
