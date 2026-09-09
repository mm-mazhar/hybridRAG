from collections.abc import Sequence
from typing import Any

import lancedb
from docling_core.transforms.chunker.base import BaseChunk
from lancedb.pydantic import LanceModel, Vector
from lancedb.table import Table

from processing.chunking import TextChunk, chunk_docling_document, chunk_document
from rag.embedder import Embedder
from rag.hybrid_search import ensure_fts_index


class ChunkMetadata(LanceModel):
    """Citation fields stored beside each vector. Names stay alphabetical."""

    filename: str | None
    page_numbers: list[int] | None
    title: str | None


def _page_numbers(chunk: BaseChunk | TextChunk) -> list[int] | None:
    meta = chunk.meta
    doc_items = getattr(meta, "doc_items", None)
    if not doc_items:
        return None
    pages: set[int] = set()
    for item in doc_items:
        for prov in getattr(item, "prov", []):
            page_no = getattr(prov, "page_no", None)
            if page_no is not None:
                pages.add(int(page_no))
    return sorted(pages) or None


def chunks_to_rows(
    chunks: Sequence[BaseChunk | TextChunk],
    vectors: list[list[float]],
    source_name: str | None = None,
) -> list[dict[str, Any]]:
    """Zip chunk text/metadata with precomputed embeddings."""
    rows: list[dict[str, Any]] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        origin = getattr(chunk.meta, "origin", None)
        origin_filename = getattr(origin, "filename", None) if origin is not None else None
        filename = source_name or origin_filename
        title = getattr(chunk.meta, "title", None)
        rows.append(
            {
                "text": chunk.text,
                "vector": vector,
                "metadata": {
                    "filename": filename,
                    "page_numbers": _page_numbers(chunk),
                    "title": title,
                },
            }
        )
    return rows


def _schema_for_dim(dim: int) -> type[LanceModel]:
    class Chunks(LanceModel):
        text: str
        vector: Vector(dim)  # type: ignore[valid-type]
        metadata: ChunkMetadata

    return Chunks


def index_chunks(
    db: lancedb.DBConnection,
    table_name: str,
    chunks: Sequence[BaseChunk | TextChunk],
    embedder: Embedder,
    mode: str = "overwrite",
    source_name: str | None = None,
) -> Table:
    """Embed chunks and write a LanceDB table. Raises if there is nothing to index."""
    if not chunks:
        raise ValueError("No chunks produced from the document.")
    texts = [chunk.text for chunk in chunks]
    vectors = embedder.embed_texts(texts)
    dim = len(vectors[0])
    schema = _schema_for_dim(dim)
    table = db.create_table(name=table_name, schema=schema, mode=mode)
    table.add(data=chunks_to_rows(chunks=chunks, vectors=vectors, source_name=source_name))
    ensure_fts_index(table)
    return table


def index_source(
    db: lancedb.DBConnection,
    table_name: str,
    source_path: str,
    max_tokens: int,
    embedder: Embedder,
    mode: str = "overwrite",
    source_name: str | None = None,
) -> Table:
    """Convert a file/URL, chunk, embed, and store."""
    chunks = chunk_document(source_path=source_path, max_tokens=max_tokens)
    return index_chunks(
        db=db,
        table_name=table_name,
        chunks=chunks,
        embedder=embedder,
        mode=mode,
        source_name=source_name,
    )


def index_docling_documents(
    db: lancedb.DBConnection,
    table_name: str,
    documents: list[Any],
    max_tokens: int,
    embedder: Embedder,
    mode: str = "overwrite",
    source_name: str | None = None,
) -> Table:
    """Chunk already-converted Docling documents (sitemap ingest)."""
    chunks: list[BaseChunk | TextChunk] = []
    for document in documents:
        chunks.extend(chunk_docling_document(document=document, max_tokens=max_tokens))
    return index_chunks(
        db=db,
        table_name=table_name,
        chunks=chunks,
        embedder=embedder,
        mode=mode,
        source_name=source_name,
    )
