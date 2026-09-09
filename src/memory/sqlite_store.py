import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SqliteMemory:
    """Document registry and per-document chat transcripts on disk."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    row_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chats (
                    document_id TEXT PRIMARY KEY,
                    messages_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                );
                """
            )

    def upsert_document(
        self,
        document_id: str,
        source_type: str,
        source_name: str,
        row_count: int,
    ) -> None:
        now = datetime.now(tz=UTC).isoformat()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, source_type, source_name, row_count, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_type = excluded.source_type,
                    source_name = excluded.source_name,
                    row_count = excluded.row_count
                """,
                (document_id, source_type, source_name, row_count, now),
            )

    def list_documents(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, source_type, source_name, row_count, created_at
                FROM documents
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def load_messages(self, document_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT messages_json FROM chats WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        if row is None:
            return []
        try:
            payload = json.loads(row["messages_json"])
        except json.JSONDecodeError:
            return []
        return payload if isinstance(payload, list) else []

    def save_messages(self, document_id: str, messages: list[dict[str, Any]]) -> None:
        now = datetime.now(tz=UTC).isoformat()
        payload = json.dumps(messages)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chats (document_id, messages_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    messages_json = excluded.messages_json,
                    updated_at = excluded.updated_at
                """,
                (document_id, payload, now),
            )

    def delete_document(self, document_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM chats WHERE document_id = ?", (document_id,))
            conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))

    def clear_documents(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM chats")
            conn.execute("DELETE FROM documents")
