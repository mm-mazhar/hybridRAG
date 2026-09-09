from types import SimpleNamespace

from langchain_core.documents import Document

from rag.lc_retrievers import parse_rewrite_lines, retrieve_documents, rrf_fuse


def test_parse_rewrite_lines_keeps_original_first() -> None:
    lines = parse_rewrite_lines("document title\nauthor name", "who wrote it?")
    assert lines[0] == "who wrote it?"
    assert "document title" in lines
    assert "author name" in lines


def test_rrf_boosts_docs_in_multiple_lists() -> None:
    alpha = Document(page_content="alpha")
    beta = Document(page_content="beta")
    fused = rrf_fuse([[alpha, beta], [alpha]], limit=2)
    assert fused[0].page_content == "alpha"


class _Embedder:
    def embed_query(self, query: str) -> list[float]:
        return [0.0, 1.0]


class _Search:
    def vector(self, _vector: list[float]) -> "_Search":
        return self

    def text(self, _query: str) -> "_Search":
        return self

    def rerank(self, reranker: object | None = None) -> "_Search":
        return self

    def limit(self, _limit: int) -> "_Search":
        return self

    def to_list(self) -> list[dict[str, object]]:
        return [{"text": "opening title page", "metadata": {"filename": "doc.pdf"}}]


class _Table:
    def list_indices(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(index_type="FTS")]

    def search(self, query: object = None, query_type: str = "auto", **_kwargs: object) -> _Search:
        return _Search()


class _RewriteLlm:
    def invoke(self, _messages: object) -> SimpleNamespace:
        return SimpleNamespace(content="document title\nmeeting date")


def test_retrieve_documents_trace_hybrid_and_multi_query() -> None:
    _docs, trace = retrieve_documents(
        table=_Table(),
        embedder=_Embedder(),
        query="what is the title?",
        limit=2,
        hybrid=True,
        multi_query=True,
        llm=_RewriteLlm(),
    )
    assert trace.hybrid is True
    assert trace.fts is True
    assert trace.multi_query is True
    assert trace.queries[0] == "what is the title?"
    assert "document title" in trace.queries
