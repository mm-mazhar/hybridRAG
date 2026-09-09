from pathlib import Path

from memory.sqlite_store import SqliteMemory


def test_upsert_and_list_documents(tmp_path: Path) -> None:
    store = SqliteMemory(tmp_path / "memory.sqlite")
    store.upsert_document("pdf_demo", "pdf", "demo.pdf", 12)
    docs = store.list_documents()
    assert len(docs) == 1
    assert docs[0]["id"] == "pdf_demo"
    assert docs[0]["row_count"] == 12


def test_save_and_load_messages(tmp_path: Path) -> None:
    store = SqliteMemory(tmp_path / "memory.sqlite")
    messages = [{"id": "1", "role": "user", "parts": [{"type": "text", "text": "hi"}]}]
    store.save_messages("pdf_demo", messages)
    assert store.load_messages("pdf_demo") == messages
    assert store.load_messages("missing") == []


def test_delete_document_removes_registry_and_chat(tmp_path: Path) -> None:
    store = SqliteMemory(tmp_path / "memory.sqlite")
    store.upsert_document("pdf_demo", "pdf", "demo.pdf", 12)
    store.save_messages("pdf_demo", [{"id": "1", "role": "user", "parts": []}])
    store.delete_document("pdf_demo")
    assert store.list_documents() == []
    assert store.load_messages("pdf_demo") == []


def test_clear_documents_wipes_all_rows(tmp_path: Path) -> None:
    store = SqliteMemory(tmp_path / "memory.sqlite")
    store.upsert_document("a", "pdf", "a.pdf", 1)
    store.upsert_document("b", "url", "https://example.com", 2)
    store.save_messages("a", [{"id": "1", "role": "user", "parts": []}])
    store.clear_documents()
    assert store.list_documents() == []
    assert store.load_messages("a") == []
