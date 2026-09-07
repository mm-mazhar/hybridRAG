# """
# 1_Extraction.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""


import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../..")))

from collections.abc import Iterator
from typing import Any

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from utils.sitemap import get_sitemap_urls

from configs import cfgs


def extract_pdf(pdf_path: str) -> tuple[str, dict[Any, Any]]:
    """
    Extract content from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        tuple: (markdown_output, json_output)
    """
    converter = DocumentConverter()
    result: ConversionResult = converter.convert(source=pdf_path)
    document: DoclingDocument = result.document
    return document.export_to_markdown(), document.export_to_dict()


def extract_html(html_path: str) -> str:
    """
    Extract content from an HTML file.

    Args:
        html_path: Path to the HTML file

    Returns:
        str: Markdown output
    """
    converter = DocumentConverter()
    result: ConversionResult = converter.convert(source=html_path)
    document: DoclingDocument = result.document
    return document.export_to_markdown()


def extract_from_sitemap(
    base_url: str, sitemap_filename: str = "sitemap.xml"
) -> list[DoclingDocument]:
    """
    Extract content from multiple pages using a sitemap.

    Args:
        base_url: Base URL of the website
        sitemap_filename: Name of the sitemap file

    Returns:
        List[DoclingDocument]: List of extracted documents
    """
    converter = DocumentConverter()
    sitemap_urls: list[str] = get_sitemap_urls(base_url=base_url, sitemap_filename=sitemap_filename)
    conv_results_iter: Iterator[ConversionResult] = converter.convert_all(source=sitemap_urls)

    docs: list[DoclingDocument] = []
    for result in conv_results_iter:
        if result.document:
            docs.append(result.document)

    return docs


def main() -> None:
    """Main function to demonstrate usage."""
    # PDF extraction example
    markdown_output, json_output = extract_pdf(pdf_path=cfgs["PDF_PATH"])
    print("PDF Extraction:")
    print(markdown_output)

    # # HTML extraction example
    # markdown_output: str = extract_html(html_path=cfgs["HTML_DOC_PATH"])
    # print("\nHTML Extraction:")
    # print(markdown_output)

    # # Sitemap extraction example
    # docs: List[DoclingDocument] = extract_from_sitemap(base_url=cfgs["BASE_URL"])
    # print("\nSitemap Extraction:")
    # print(f"Extracted {len(docs)} documents")


if __name__ == "__main__":
    main()
