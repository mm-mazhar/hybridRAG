"""Thin LangChain retriever adapters around LanceDB. Chat still lives in Next.js."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI
from pydantic import ConfigDict

from core.settings import AppSettings
from rag.hybrid_search import ensure_fts_index, search_hybrid, search_keyword, search_vector
from rag.retriever import RetrievalTrace, hit_from_row

logger = logging.getLogger(__name__)

_REWRITE_SYSTEM = (
    "Rewrite the user question into 2 short keyword search queries for a document index. "
    "Prefer titles, names, dates, and distinctive nouns. "
    "Return only the queries, one per line, with no numbering."
)


class LanceVectorRetriever(BaseRetriever):
    """Nearest-neighbor search. Safe to pass into a future LangChain agent as a tool."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    table: Any
    embedder: Any
    k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        vector = self.embedder.embed_query(query)
        return [document_from_row(row) for row in search_vector(self.table, vector, self.k)]


class LanceKeywordRetriever(BaseRetriever):
    """Full-text search over chunk text."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    table: Any
    k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        return [document_from_row(row) for row in search_keyword(self.table, query, self.k)]


class LanceHybridRetriever(BaseRetriever):
    """LanceDB hybrid search (vector + FTS + RRF)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    table: Any
    embedder: Any
    k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        vector = self.embedder.embed_query(query)
        outcome = search_hybrid(self.table, vector, query, self.k)
        return [document_from_row(row) for row in outcome.rows]


def document_from_row(row: dict[str, object]) -> Document:
    hit = hit_from_row(row)
    return Document(
        page_content=hit.text,
        metadata={
            "filename": hit.filename,
            "page_numbers": hit.page_numbers,
            "title": hit.title,
            "source": hit.source,
            "row": row,
        },
    )


def rrf_fuse(
    ranked_lists: list[list[Document]],
    limit: int,
    rank_constant: int = 60,
) -> list[Document]:
    """Fuse retriever lists with reciprocal rank fusion (ensemble pattern)."""
    scores: dict[str, float] = {}
    docs: dict[str, Document] = {}
    for results in ranked_lists:
        for rank, doc in enumerate(results, start=1):
            key = doc.page_content.strip()
            if not key:
                continue
            scores[key] = scores.get(key, 0.0) + 1.0 / (rank_constant + rank)
            docs.setdefault(key, doc)
    ordered = sorted(scores, key=lambda key: scores[key], reverse=True)
    return [docs[key] for key in ordered[:limit]]


def parse_rewrite_lines(text: str, original: str) -> list[str]:
    """Keep the original query plus unique rewritten lines."""
    lines = [original]
    seen = {original.strip().lower()}
    for raw in text.splitlines():
        item = raw.strip().lstrip("0123456789.-) ").strip()
        if not item or item.lower() in seen:
            continue
        seen.add(item.lower())
        lines.append(item)
        if len(lines) >= 4:
            break
    return lines


def create_rewrite_llm(settings: AppSettings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm.model,
        api_key=settings.llm_api_key,
        base_url=settings.llm.base_url,
        temperature=0,
        max_tokens=200,
        default_headers={
            "HTTP-Referer": settings.app.http_referer,
            "X-OpenRouter-Title": settings.app.title,
        },
    )


def rewrite_queries(llm: Any, query: str) -> list[str]:
    try:
        response = llm.invoke(
            [
                {"role": "system", "content": _REWRITE_SYSTEM},
                {"role": "user", "content": query},
            ]
        )
    except Exception as exc:
        logger.warning("Query rewrite failed, using the original question: %s", exc)
        return [query]
    content = response.content
    text = content if isinstance(content, str) else ""
    return parse_rewrite_lines(text, query)


def retrieve_documents(
    table: Any,
    embedder: Any,
    query: str,
    limit: int,
    *,
    hybrid: bool = True,
    multi_query: bool = False,
    llm: Any = None,
) -> tuple[list[Document], RetrievalTrace]:
    """Ensemble (vector + keyword, and native hybrid) with optional multi-query rewrite."""
    fts = ensure_fts_index(table)
    queries = rewrite_queries(llm, query) if multi_query and llm is not None else [query]
    vector_retriever = LanceVectorRetriever(table=table, embedder=embedder, k=limit)
    keyword_retriever = LanceKeywordRetriever(table=table, k=limit)
    used_hybrid = False
    per_query: list[list[Document]] = []
    for item in queries:
        ensemble = rrf_fuse(
            [vector_retriever.invoke(item), keyword_retriever.invoke(item)],
            limit=limit,
        )
        if hybrid:
            outcome = search_hybrid(table, embedder.embed_query(item), item, limit)
            used_hybrid = used_hybrid or outcome.used_hybrid
            hybrid_docs = [document_from_row(row) for row in outcome.rows]
            per_query.append(rrf_fuse([hybrid_docs, ensemble], limit=limit))
        else:
            per_query.append(ensemble)
    trace = RetrievalTrace(
        hybrid=used_hybrid,
        fts=fts,
        multi_query=len(queries) > 1,
        queries=queries,
    )
    logger.info(
        "retrieve hybrid=%s fts=%s multi_query=%s queries=%s",
        trace.hybrid,
        trace.fts,
        trace.multi_query,
        trace.queries,
    )
    return rrf_fuse(per_query, limit=limit), trace
