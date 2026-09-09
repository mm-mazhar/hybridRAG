from collections.abc import Sequence
from dataclasses import dataclass, field
from types import SimpleNamespace

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc.document import DoclingDocument

from processing.sitemap import get_sitemap_urls
from processing.tokenizer import OpenAITokenizerWrapper

_CHUNK_TOKEN_CAP = 512


@dataclass
class TextChunk:
    """Minimal chunk used when HybridChunker yields nothing."""

    text: str
    meta: SimpleNamespace = field(
        default_factory=lambda: SimpleNamespace(origin=None, title=None, doc_items=None)
    )


def convert_source(source_path: str) -> DoclingDocument:
    """Convert a local file or URL into a Docling document."""
    converter = DocumentConverter()
    try:
        result: ConversionResult = converter.convert(source=source_path)
    except Exception as exc:
        raise ValueError(f"Could not convert this source: {exc}") from exc
    if result.document is None:
        raise ValueError("Document conversion produced no content.")
    return result.document


def extract_from_sitemap(
    base_url: str, sitemap_filename: str = "sitemap.xml"
) -> list[DoclingDocument]:
    """Convert sitemap page URLs (or the origin if no sitemap exists)."""
    converter = DocumentConverter()
    urls = get_sitemap_urls(base_url=base_url, sitemap_filename=sitemap_filename)
    documents: list[DoclingDocument] = []
    for url in urls:
        try:
            result = converter.convert(source=url)
        except Exception:
            continue
        if result.document is not None:
            documents.append(result.document)
    return documents


def chunk_document(source_path: str, max_tokens: int) -> Sequence[BaseChunk | TextChunk]:
    """Convert then hybrid-chunk a document."""
    document = convert_source(source_path=source_path)
    return chunk_docling_document(document=document, max_tokens=max_tokens)


def chunk_docling_document(
    document: DoclingDocument, max_tokens: int
) -> Sequence[BaseChunk | TextChunk]:
    """Split an already-converted Docling document."""
    chunk_limit = min(max_tokens, _CHUNK_TOKEN_CAP)
    chunks: list[BaseChunk | TextChunk] = []
    try:
        chunker = HybridChunker(
            tokenizer=OpenAITokenizerWrapper(max_length=max_tokens),
            max_tokens=chunk_limit,
            merge_peers=True,
        )
        chunks = [chunk for chunk in chunker.chunk(dl_doc=document) if chunk.text.strip()]
    except (NotImplementedError, ValueError, RuntimeError, TypeError):
        chunks = []
    if chunks:
        return chunks
    fallback = fallback_text_chunks(_document_text(document), chunk_limit)
    if fallback:
        return fallback
    raise ValueError("No chunks produced from the document.")


def _document_text(document: DoclingDocument) -> str:
    export_text = getattr(document, "export_to_text", None)
    if callable(export_text):
        text = str(export_text() or "").strip()
        if text:
            return text
    export_md = getattr(document, "export_to_markdown", None)
    if callable(export_md):
        return str(export_md() or "").strip()
    return ""


def fallback_text_chunks(text: str, max_tokens: int) -> list[TextChunk]:
    """Pack plain text into token windows when structure-aware chunking is empty."""
    stripped = text.strip()
    if not stripped:
        return []
    tokenizer = OpenAITokenizerWrapper(max_length=max_tokens)
    windows: list[str] = []
    current = ""
    for paragraph in [part.strip() for part in stripped.split("\n") if part.strip()]:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(tokenizer.tokenize(candidate)) <= max_tokens:
            current = candidate
            continue
        if current:
            windows.append(current)
        if len(tokenizer.tokenize(paragraph)) <= max_tokens:
            current = paragraph
            continue
        windows.extend(_split_long_paragraph(paragraph, max_tokens, tokenizer))
        current = ""
    if current:
        windows.append(current)
    return [TextChunk(text=item) for item in windows]


def _split_long_paragraph(
    paragraph: str, max_tokens: int, tokenizer: OpenAITokenizerWrapper
) -> list[str]:
    words = paragraph.split()
    parts: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(tokenizer.tokenize(candidate)) <= max_tokens:
            current = candidate
            continue
        if current:
            parts.append(current)
        current = word
    if current:
        parts.append(current)
    return parts
