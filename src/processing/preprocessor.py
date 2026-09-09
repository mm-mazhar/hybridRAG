from docling_core.types.doc.document import DoclingDocument

from processing.chunking import convert_source, extract_from_sitemap


def load_document(source_path: str) -> DoclingDocument:
    """Load a PDF, HTML file, or URL as a Docling document."""
    return convert_source(source_path=source_path)


def load_sitemap(base_url: str, sitemap_filename: str = "sitemap.xml") -> list[DoclingDocument]:
    """Load every page listed in a website sitemap."""
    return extract_from_sitemap(base_url=base_url, sitemap_filename=sitemap_filename)
