import logging

from lancedb.table import Table

from core.settings import AppSettings
from rag.embedder import Embedder
from rag.retriever import RetrievalBundle, retrieve_with_trace

logger = logging.getLogger(__name__)


def retrieve_for_query(
    table: Table,
    embedder: Embedder,
    query: str,
    limit: int,
    settings: AppSettings | None = None,
) -> RetrievalBundle:
    """Orchestrate retrieval for the FastAPI retrieve route."""
    hybrid = True
    multi_query = False
    llm = None
    if settings is not None:
        hybrid = settings.vector_db.hybrid
        multi_query = settings.vector_db.multi_query
        if multi_query:
            from rag.lc_retrievers import create_rewrite_llm

            try:
                llm = create_rewrite_llm(settings)
            except Exception as exc:
                logger.warning("multi_query disabled: rewrite LLM unavailable: %s", exc)
                llm = None
    return retrieve_with_trace(
        table=table,
        embedder=embedder,
        query=query,
        limit=limit,
        hybrid=hybrid,
        multi_query=multi_query and llm is not None,
        llm=llm,
    )
