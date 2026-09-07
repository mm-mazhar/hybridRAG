# """
# 3_embedding.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""

import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../..")))

from collections.abc import Iterator
from typing import Any

import lancedb
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from lancedb.table import Table
from utils.tokenizer import OpenAITokenizerWrapper

from configs import cfgs

load_dotenv()


class ChunkMetadata(LanceModel):
    """
    Metadata schema for chunks.
    Fields must be in alphabetical order (Pydantic requirement).
    """

    filename: str | None
    page_numbers: list[int] | None
    title: str | None


def get_chunks(max_tokens: int, source_path: str) -> list[BaseChunk]:
    """
    Extract and chunk the document.

    Args:
        max_tokens: Maximum tokens per chunk
        source_path: Path to the source document

    Returns:
        List[BaseChunk]: List of document chunks
    """
    tokenizer = OpenAITokenizerWrapper()
    converter = DocumentConverter()
    result: ConversionResult = converter.convert(source=source_path)

    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=max_tokens,
        merge_peers=True,
    )

    chunk_iter: Iterator[BaseChunk] = chunker.chunk(dl_doc=result.document)
    return list(chunk_iter)


def initialize_database(db_path: str) -> lancedb.DBConnection:
    """
    Initialize LanceDB database.

    Args:
        db_path: Path to the database

    Returns:
        lancedb.DBConnection: Database connection
    """
    os.makedirs(name=db_path, exist_ok=True)
    return lancedb.connect(uri=db_path)


def create_table(
    db: lancedb.DBConnection,
    table_name: str,
    llm_provider: str,
    embed_model: str,
    mode: str = "overwrite",
) -> Table:
    """
    Create a LanceDB table with the specified schema.

    Args:
        db: Database connection
        table_name: Name of the table
        llm_provider: Name of the LLM provider
        embed_model: Name of the embedding model
        mode: Table creation mode

    Returns:
        Table: Created LanceDB table
    """
    # Get the embedding function
    func: Any = get_registry().get(name=llm_provider).create(name=embed_model)

    # Create dynamic Chunks class with proper Vector initialization
    class Chunks(LanceModel):
        """Schema for the main chunks table."""

        text: str = func.SourceField()
        vector: Vector(dim=func.ndims()) = func.VectorField()  # type: ignore
        metadata: ChunkMetadata

    return db.create_table(
        name=table_name,
        schema=Chunks,
        mode=mode,
    )


def process_chunks(chunks: list[BaseChunk]) -> list[dict[str, Any]]:
    """
    Process chunks into the format required for the database.

    Args:
        chunks: List of document chunks

    Returns:
        List[Dict[str, Any]]: Processed chunks ready for database insertion
    """
    return [
        {
            "text": chunk.text,
            "metadata": {
                "filename": chunk.meta.origin.filename,  # type: ignore
                "page_numbers": [
                    page_no
                    for page_no in sorted(
                        set(
                            prov.page_no
                            for item in chunk.meta.doc_items  # type: ignore
                            for prov in item.prov
                        )
                    )
                ]
                or None,
                "title": getattr(chunk.meta, "title", None),
            },
        }
        for chunk in chunks
    ]


def create_embeddings(
    source_path: str,
    max_tokens: int,
    db_path: str,
    table_name: str,
    llm_provider: str,
    embed_model: str,
    mode: str = "overwrite",  # Add mode parameter with default value
) -> Table:
    """
    Main function to create embeddings from a document.

    Args:
        source_path: Path to the source document
        max_tokens: Maximum tokens per chunk
        db_path: Path to the database
        table_name: Name of the table
        llm_provider: Name of the LLM provider
        embed_model: Name of the embedding model
        mode: Table creation mode ("create" or "overwrite")

    Returns:
        Table: Created and populated LanceDB table
    """
    # Get document chunks
    chunks: list[BaseChunk] = get_chunks(max_tokens=max_tokens, source_path=source_path)

    # Initialize database
    db: lancedb.DBConnection = initialize_database(db_path=db_path)

    # Create table
    table: Table = create_table(
        db=db,
        table_name=table_name,
        llm_provider=llm_provider,
        embed_model=embed_model,
        mode=mode,
    )

    # Process and add chunks
    processed_chunks: list[dict[str, Any]] = process_chunks(chunks=chunks)
    table.add(data=processed_chunks)

    return table


def main() -> None:
    """Main function to demonstrate usage."""
    db_path: str = os.path.abspath(
        path=os.path.join(os.path.dirname(p=__file__), "../..", cfgs["VECTOR_DB"]["URI"])
    )

    table: Table = create_embeddings(
        source_path=cfgs["PDF_PATH"],
        max_tokens=cfgs["LLM"]["MAX_TOKENS"],
        db_path=db_path,
        table_name=cfgs["VECTOR_DB"]["TABLE_NAME"],
        llm_provider=cfgs["LLM"]["PROVIDER"],
        embed_model=cfgs["EMBEDDINGS"]["MODEL"],
    )

    print(f"Created table with {table.count_rows()} rows")


if __name__ == "__main__":
    main()
