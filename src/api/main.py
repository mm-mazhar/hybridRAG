from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import AppContext
from api.errors import register_exception_handlers
from api.routes_documents import router as documents_router
from api.routes_ingest import router as ingest_router
from api.routes_memory import router as memory_router
from api.routes_retrieve import router as retrieve_router
from core.llm_client import create_embedding_client
from core.paths import project_root
from core.settings import get_settings
from memory.sqlite_store import SqliteMemory
from rag.embedder import Embedder
from rag.vector_store import connect


def configure_logging() -> None:
    import logging.config

    root = project_root()
    config_path = root / "config" / "logging_config.yaml"
    if not config_path.is_file():
        return
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = payload.get("handlers", {}).get("file")
    if isinstance(file_handler, dict):
        file_handler["filename"] = str(log_dir / "app.log")
    logging.config.dictConfig(payload)
    logging.getLogger(__name__).info("Logging to %s", log_dir / "app.log")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    embed_client = create_embedding_client(settings)
    app.state.ctx = AppContext(
        settings=settings,
        embed_client=embed_client,
        embedder=Embedder.from_settings(settings, embed_client),
        db=connect(settings.vector_db_path),
        memory=SqliteMemory(Path(settings.memory_db_path)),
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="hybridRAG",
        description="Hybrid RAG ingest and retrieve API (LanceDB + OpenAI-compatible embeddings).",
        lifespan=lifespan,
    )
    origin = getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(documents_router, prefix="/api")
    app.include_router(ingest_router, prefix="/api")
    app.include_router(retrieve_router, prefix="/api")
    app.include_router(memory_router, prefix="/api")
    return app


app = create_app()
