import re
from urllib.parse import urlparse

import lancedb
from fastapi import APIRouter, Depends, HTTPException

from api.deps import AppContext, get_ctx
from api.schemas import DocumentDeleted, DocumentOut, DocumentsCleared, PublicConfigResponse
from memory.sqlite_store import SqliteMemory
from rag.vector_store import drop_table, list_tables, open_table

router = APIRouter()

_DOCUMENT_ID = re.compile(r"^[a-z0-9_]{1,200}$")


def parse_document_id(document_id: str) -> str:
    if not _DOCUMENT_ID.fullmatch(document_id):
        raise HTTPException(status_code=400, detail="Invalid document id.")
    return document_id


def remove_indexed_document(
    db: lancedb.DBConnection,
    memory: SqliteMemory,
    document_id: str,
) -> bool:
    """Drop one LanceDB table and its SQLite registry/chat rows."""
    tables = list_tables(db)
    known = document_id in tables or any(
        row["id"] == document_id for row in memory.list_documents()
    )
    if not known:
        return False
    if document_id in tables:
        drop_table(db, document_id)
    memory.delete_document(document_id)
    return True


def clear_indexed_documents(db: lancedb.DBConnection, memory: SqliteMemory) -> int:
    """Drop every LanceDB table and wipe the document registry."""
    names = list_tables(db)
    for name in names:
        drop_table(db, name)
    memory.clear_documents()
    return len(names)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/config", response_model=PublicConfigResponse)
def public_config(ctx: AppContext = Depends(get_ctx)) -> PublicConfigResponse:
    return PublicConfigResponse(
        model=ctx.settings.llm.model,
        models=ctx.settings.llm.models,
        embedding_model=ctx.settings.embeddings.model,
    )


@router.get("/documents", response_model=list[DocumentOut])
def documents(ctx: AppContext = Depends(get_ctx)) -> list[DocumentOut]:
    tables = list_tables(ctx.db)
    stored = {item["id"]: item for item in ctx.memory.list_documents()}
    result: list[DocumentOut] = []
    for name in tables:
        meta = stored.get(name)
        if meta:
            result.append(DocumentOut.model_validate(meta))
            continue
        table = open_table(ctx.db, name)
        result.append(
            DocumentOut(
                id=name,
                source_type="unknown",
                source_name=name,
                row_count=table.count_rows(),
                created_at=None,
            )
        )
    return result


@router.delete("/documents/{document_id}", response_model=DocumentDeleted)
def delete_document(
    document_id: str,
    ctx: AppContext = Depends(get_ctx),
) -> DocumentDeleted:
    parsed = parse_document_id(document_id)
    if not remove_indexed_document(ctx.db, ctx.memory, parsed):
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentDeleted(document_id=parsed)


@router.delete("/documents", response_model=DocumentsCleared)
def delete_documents(ctx: AppContext = Depends(get_ctx)) -> DocumentsCleared:
    dropped = clear_indexed_documents(ctx.db, ctx.memory)
    return DocumentsCleared(dropped=dropped)


def require_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
