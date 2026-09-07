# """
# 2_chunking.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""


import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../..")))

from collections.abc import Iterator

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from dotenv import load_dotenv
from utils.tokenizer import OpenAITokenizerWrapper

from configs import cfgs

load_dotenv()


def initialize_chunker(max_tokens: int) -> HybridChunker:
    """
    Initialize the HybridChunker with OpenAI tokenizer.

    Args:
        max_tokens: Maximum tokens per chunk

    Returns:
        HybridChunker: Initialized chunker
    """
    tokenizer = OpenAITokenizerWrapper()
    return HybridChunker(
        tokenizer=tokenizer,
        max_tokens=max_tokens,
        merge_peers=True,
    )


def chunk_document(source_path: str, max_tokens: int) -> list[BaseChunk]:
    """
    Convert document and split it into chunks.

    Args:
        source_path: Path to the source document
        max_tokens: Maximum tokens per chunk

    Returns:
        List[BaseChunk]: List of document chunks
    """
    # Convert document
    converter = DocumentConverter()
    result: ConversionResult = converter.convert(source=source_path)

    # Initialize chunker and process document
    chunker: HybridChunker = initialize_chunker(max_tokens=max_tokens)
    chunk_iter: Iterator[BaseChunk] = chunker.chunk(dl_doc=result.document)
    return list(chunk_iter)


def main() -> None:
    """Main function to demonstrate usage."""
    chunks: list[BaseChunk] = chunk_document(
        source_path=cfgs["PDF_PATH"], max_tokens=cfgs["MAX_TOKENS"]
    )
    print(f"Created {len(chunks)} chunks")


if __name__ == "__main__":
    main()
