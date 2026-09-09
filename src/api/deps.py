from dataclasses import dataclass

import lancedb
from fastapi import Request
from openai import OpenAI

from core.settings import AppSettings
from memory.sqlite_store import SqliteMemory
from rag.embedder import Embedder


@dataclass
class AppContext:
    settings: AppSettings
    embed_client: OpenAI
    embedder: Embedder
    db: lancedb.DBConnection
    memory: SqliteMemory


def get_ctx(request: Request) -> AppContext:
    return request.app.state.ctx
