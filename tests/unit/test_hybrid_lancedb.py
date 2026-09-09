from pathlib import Path

from rag.hybrid_search import ensure_fts_index
from rag.retriever import retrieve_chunks
from rag.vector_store import connect


class _BiasEmbedder:
    """Points at the robotics chunk so keyword search must earn the title row."""

    def embed_query(self, query: str) -> list[float]:
        return [0.0, 1.0]


def test_hybrid_surfaces_keyword_title_chunk(tmp_path: Path) -> None:
    db = connect(tmp_path / "vectordb")
    table = db.create_table(
        "doc",
        [
            {
                "text": "BOARD of ELEMENTARY and SECONDARY EDUCATION Meeting of January 15, 2014",
                "vector": [1.0, 0.0],
                "metadata": {
                    "filename": "minutes.pdf",
                    "page_numbers": [1],
                    "title": None,
                },
            },
            {
                "text": "Robotics display in the lobby agenda item five",
                "vector": [0.0, 1.0],
                "metadata": {
                    "filename": "minutes.pdf",
                    "page_numbers": [5],
                    "title": None,
                },
            },
        ],
    )
    assert ensure_fts_index(table)
    hits = retrieve_chunks(
        table=table,
        embedder=_BiasEmbedder(),
        query="what is the title of the meeting minutes",
        limit=2,
        hybrid=True,
        multi_query=False,
    )
    joined = " ".join(hit.text for hit in hits)
    assert "BOARD" in joined or "January" in joined
