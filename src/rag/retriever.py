from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lancedb.table import Table

from rag.embedder import QueryEmbedder

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

_PREFIX_ROWS = 3


@dataclass(frozen=True)
class RetrievalTrace:
    """What actually ran for one retrieve, after silent fallbacks."""

    hybrid: bool
    fts: bool
    multi_query: bool
    queries: list[str]


@dataclass(frozen=True)
class RetrievalBundle:
    hits: list[ChunkHit]
    trace: RetrievalTrace


@dataclass(frozen=True)
class ChunkHit:
    """A retrieved passage plus citation metadata."""

    text: str
    filename: str | None
    page_numbers: list[int] | None
    title: str | None

    @property
    def source(self) -> str:
        parts: list[str] = []
        if self.filename:
            parts.append(self.filename)
        if self.page_numbers:
            pages = ", ".join(str(page) for page in self.page_numbers)
            parts.append(f"p. {pages}")
        return " — ".join(parts) if parts else "unknown source"


def _metadata_dict(row: dict[str, object]) -> dict[str, object]:
    meta = row.get("metadata")
    if isinstance(meta, dict):
        return meta
    return {}


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_int_list(value: object) -> list[int] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [int(item) for item in value]
    to_list = getattr(value, "tolist", None)
    if callable(to_list):
        converted = to_list()
        if isinstance(converted, list):
            return [int(item) for item in converted]
    return None


def hit_from_row(row: dict[str, object]) -> ChunkHit:
    """Map a LanceDB row (search hit or table prefix) to a ChunkHit."""
    meta = _metadata_dict(row)
    return ChunkHit(
        text=str(row.get("text", "")),
        filename=_optional_str(meta.get("filename")),
        page_numbers=_as_int_list(meta.get("page_numbers")),
        title=_optional_str(meta.get("title")),
    )


def merge_search_rows(
    prefix_rows: list[dict[str, object]],
    semantic_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Keep document-start rows, then unique nearest-neighbor hits."""
    merged: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in [*prefix_rows, *semantic_rows]:
        text = str(row.get("text", "")).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        merged.append(row)
    return merged


def _prefix_rows(table: Table, count: int) -> list[dict[str, object]]:
    if count <= 0:
        return []
    to_pandas = getattr(table, "to_pandas", None)
    if not callable(to_pandas):
        return []
    frame = to_pandas()
    records = frame.head(count).to_dict(orient="records")
    return [dict(record) for record in records]


def retrieve_chunks(
    table: Table,
    embedder: QueryEmbedder,
    query: str,
    limit: int,
    *,
    hybrid: bool = True,
    multi_query: bool = False,
    llm: ChatOpenAI | None = None,
) -> list[ChunkHit]:
    """Return opening chunks plus hybrid / ensemble hits for the query."""
    return retrieve_with_trace(
        table=table,
        embedder=embedder,
        query=query,
        limit=limit,
        hybrid=hybrid,
        multi_query=multi_query,
        llm=llm,
    ).hits


def retrieve_with_trace(
    table: Table,
    embedder: QueryEmbedder,
    query: str,
    limit: int,
    *,
    hybrid: bool = True,
    multi_query: bool = False,
    llm: ChatOpenAI | None = None,
) -> RetrievalBundle:
    """Return hits plus whether hybrid / multi-query actually ran."""
    from rag.lc_retrievers import retrieve_documents

    prefix_rows = _prefix_rows(table, _PREFIX_ROWS)
    documents, trace = retrieve_documents(
        table=table,
        embedder=embedder,
        query=query,
        limit=limit,
        hybrid=hybrid,
        multi_query=multi_query,
        llm=llm,
    )
    search_rows: list[dict[str, object]] = []
    for document in documents:
        row = document.metadata.get("row")
        if isinstance(row, dict):
            search_rows.append(row)
            continue
        search_rows.append({"text": document.page_content, "metadata": document.metadata})
    hits = [hit_from_row(row) for row in merge_search_rows(prefix_rows, search_rows)]
    return RetrievalBundle(hits=hits, trace=trace)
