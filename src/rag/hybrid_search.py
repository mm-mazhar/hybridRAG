from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from lancedb.rerankers import RRFReranker
from lancedb.table import Table

logger = logging.getLogger(__name__)

_FTS_TOKEN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class HybridSearchOutcome:
    """Rows plus whether LanceDB actually ran vector+FTS hybrid (not vector fallback)."""

    rows: list[dict[str, object]]
    used_hybrid: bool


def sanitize_fts_query(query: str) -> str:
    """Keep alphanumeric tokens so Tantivy-style query syntax cannot break FTS."""
    return " ".join(_FTS_TOKEN.findall(query))


def has_fts_index(table: Table) -> bool:
    try:
        indices = table.list_indices()
    except Exception:
        return False
    for item in indices:
        index_type = str(getattr(item, "index_type", "")).upper()
        if index_type == "FTS":
            return True
    return False


def ensure_fts_index(table: Table) -> bool:
    """Create a native inverted index on `text` when the table has none."""
    if has_fts_index(table):
        return True
    try:
        table.create_fts_index("text", replace=True, use_tantivy=False)
        return True
    except Exception as exc:
        logger.warning("Could not create FTS index: %s", exc)
        return False


def search_vector(table: Table, vector: list[float], limit: int) -> list[dict[str, object]]:
    return table.search(vector).limit(limit).to_list()


def search_keyword(table: Table, query: str, limit: int) -> list[dict[str, object]]:
    fts_query = sanitize_fts_query(query)
    if not fts_query or not ensure_fts_index(table):
        return []
    try:
        return table.search(fts_query, query_type="fts").limit(limit).to_list()
    except Exception as exc:
        logger.warning("Keyword search failed: %s", exc)
        return []


def search_hybrid(table: Table, vector: list[float], query: str, limit: int) -> HybridSearchOutcome:
    """Vector + full-text search fused with reciprocal rank fusion."""
    fts_query = sanitize_fts_query(query)
    if not fts_query or not ensure_fts_index(table):
        return HybridSearchOutcome(rows=search_vector(table, vector, limit), used_hybrid=False)
    try:
        rows = (
            table.search(query_type="hybrid")
            .vector(vector)
            .text(fts_query)
            .rerank(reranker=RRFReranker())
            .limit(limit)
            .to_list()
        )
        return HybridSearchOutcome(rows=rows, used_hybrid=True)
    except Exception as exc:
        logger.warning("Hybrid search failed, using vector search: %s", exc)
        return HybridSearchOutcome(rows=search_vector(table, vector, limit), used_hybrid=False)
