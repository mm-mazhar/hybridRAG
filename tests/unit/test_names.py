import pytest

from processing.names import clean_table_name, domain_label


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("My File.PDF", "my_file_pdf"),
        ("hello---world", "hello_world"),
        ("Docling Docs", "docling_docs"),
    ],
)
def test_clean_table_name(raw: str, expected: str) -> None:
    assert clean_table_name(raw) == expected


def test_domain_label_strips_www_and_tld() -> None:
    assert domain_label("www.example.com", [".com", ".io"]) == "example"
