from types import SimpleNamespace

import pandas as pd

from inference.inference_engine import retrieve_for_query
from rag.retriever import ChunkHit

_ROWS: list[dict[str, object]] = [
    {
        "text": "LanceDB stores vectors on disk.",
        "metadata": {
            "filename": "lancedb.md",
            "page_numbers": [3],
            "title": "Storage",
        },
    }
]


class _FakeEmbedder:
    def embed_query(self, query: str) -> list[float]:
        return [0.1, 0.2]


class _FakeQuery:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def vector(self, _vector: list[float]) -> "_FakeQuery":
        return self

    def text(self, _query: str) -> "_FakeQuery":
        return self

    def rerank(self, reranker: object | None = None) -> "_FakeQuery":
        return self

    def limit(self, _limit: int) -> "_FakeQuery":
        return self

    def to_list(self) -> list[dict[str, object]]:
        return self._rows


class _FakeTable:
    def list_indices(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(index_type="FTS", name="text_idx")]

    def search(
        self, query: object = None, query_type: str = "auto", **_kwargs: object
    ) -> _FakeQuery:
        return _FakeQuery(_ROWS)

    def to_pandas(self) -> object:
        return pd.DataFrame(
            [
                {
                    "text": "Opening header of the document.",
                    "metadata": {
                        "filename": "guide.pdf",
                        "page_numbers": [1],
                        "title": None,
                    },
                }
            ]
        )


def test_retrieve_for_query_maps_rows() -> None:
    bundle = retrieve_for_query(
        table=_FakeTable(),  # type: ignore[arg-type]
        embedder=_FakeEmbedder(),  # type: ignore[arg-type]
        query="where are vectors stored?",
        limit=3,
    )
    hits = bundle.hits
    assert hits[0].text == "Opening header of the document."
    assert hits[1] == ChunkHit(
        text="LanceDB stores vectors on disk.",
        filename="lancedb.md",
        page_numbers=[3],
        title="Storage",
    )
    assert bundle.trace.hybrid is True
    assert bundle.trace.fts is True
    assert bundle.trace.multi_query is False
