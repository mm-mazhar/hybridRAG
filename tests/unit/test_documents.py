from pathlib import Path

import lancedb
import pytest
from fastapi import HTTPException

from api.routes_documents import (
    clear_indexed_documents,
    parse_document_id,
    remove_indexed_document,
)
from memory.sqlite_store import SqliteMemory
from rag.vector_store import connect, list_tables


def _seed_table(db: lancedb.DBConnection, name: str) -> None:
    db.create_table(
        name,
        [{"text": "hello", "vector": [0.1, 0.2], "metadata": {"filename": f"{name}.pdf"}}],
    )


def test_parse_document_id_rejects_unsafe_names() -> None:
    with pytest.raises(HTTPException) as caught:
        parse_document_id("../secret")
    assert caught.value.status_code == 400
    assert parse_document_id("pdf_meetingminutes2_pdf") == "pdf_meetingminutes2_pdf"


def test_remove_indexed_document_drops_table_and_memory(tmp_path: Path) -> None:
    db = connect(tmp_path / "vectordb")
    memory = SqliteMemory(tmp_path / "memory.sqlite")
    _seed_table(db, "pdf_demo")
    memory.upsert_document("pdf_demo", "pdf", "demo.pdf", 1)
    memory.save_messages("pdf_demo", [{"id": "1", "role": "user", "parts": []}])

    assert remove_indexed_document(db, memory, "pdf_demo") is True
    assert list_tables(db) == []
    assert memory.list_documents() == []
    assert memory.load_messages("pdf_demo") == []


def test_remove_indexed_document_missing_returns_false(tmp_path: Path) -> None:
    db = connect(tmp_path / "vectordb")
    memory = SqliteMemory(tmp_path / "memory.sqlite")
    assert remove_indexed_document(db, memory, "missing") is False


def test_clear_indexed_documents_drops_every_table(tmp_path: Path) -> None:
    db = connect(tmp_path / "vectordb")
    memory = SqliteMemory(tmp_path / "memory.sqlite")
    _seed_table(db, "pdf_one")
    _seed_table(db, "url_two")
    memory.upsert_document("pdf_one", "pdf", "one.pdf", 1)
    memory.upsert_document("orphan", "url", "https://example.com", 1)

    dropped = clear_indexed_documents(db, memory)
    assert dropped == 2
    assert list_tables(db) == []
    assert memory.list_documents() == []
