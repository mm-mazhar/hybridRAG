from rag.retriever import ChunkHit, merge_search_rows


def test_source_includes_filename_and_pages() -> None:
    hit = ChunkHit(
        text="hello",
        filename="guide.pdf",
        page_numbers=[1, 2],
        title="Intro",
    )
    assert hit.source == "guide.pdf — p. 1, 2"


def test_source_unknown_without_metadata() -> None:
    hit = ChunkHit(text="hello", filename=None, page_numbers=None, title=None)
    assert hit.source == "unknown source"


def test_merge_search_rows_keeps_prefix_then_unique_semantic() -> None:
    prefix: list[dict[str, object]] = [
        {"text": "Meeting of January 15, 2014"},
        {"text": "Board called to order"},
    ]
    semantic: list[dict[str, object]] = [
        {"text": "Agenda item 5"},
        {"text": "Meeting of January 15, 2014"},
    ]
    merged = merge_search_rows(prefix, semantic)
    assert [row["text"] for row in merged] == [
        "Meeting of January 15, 2014",
        "Board called to order",
        "Agenda item 5",
    ]
