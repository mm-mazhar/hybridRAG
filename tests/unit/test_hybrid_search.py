from types import SimpleNamespace

from rag.hybrid_search import sanitize_fts_query, search_hybrid


def test_sanitize_keeps_keywords() -> None:
    cleaned = sanitize_fts_query("what is the title of the pdf?")
    assert "title" in cleaned
    assert "pdf" in cleaned
    assert "?" not in cleaned


def test_sanitize_empty_punctuation_only() -> None:
    assert sanitize_fts_query("???") == ""


class _Query:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def vector(self, _vector: list[float]) -> "_Query":
        return self

    def text(self, _query: str) -> "_Query":
        return self

    def rerank(self, reranker: object | None = None) -> "_Query":
        return self

    def limit(self, _limit: int) -> "_Query":
        return self

    def to_list(self) -> list[dict[str, object]]:
        return self._rows


class _HybridTable:
    def list_indices(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(index_type="FTS")]

    def search(self, query: object = None, query_type: str = "auto", **_kwargs: object) -> _Query:
        return _Query([{"text": "hybrid hit"}])


class _NoFtsTable:
    def list_indices(self) -> list[SimpleNamespace]:
        return []

    def create_fts_index(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("no fts")

    def search(self, query: object = None, query_type: str = "auto", **_kwargs: object) -> _Query:
        return _Query([{"text": "vector hit"}])


def test_search_hybrid_reports_used_hybrid() -> None:
    outcome = search_hybrid(_HybridTable(), [0.1, 0.2], "meeting title", 3)  # type: ignore[arg-type]
    assert outcome.used_hybrid is True
    assert outcome.rows[0]["text"] == "hybrid hit"


def test_search_hybrid_falls_back_without_fts() -> None:
    outcome = search_hybrid(_NoFtsTable(), [0.1, 0.2], "meeting title", 3)  # type: ignore[arg-type]
    assert outcome.used_hybrid is False
    assert outcome.rows[0]["text"] == "vector hit"
