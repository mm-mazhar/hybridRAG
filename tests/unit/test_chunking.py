from processing.chunking import fallback_text_chunks


def test_fallback_text_chunks_packs_paragraphs() -> None:
    text = "Title of the minutes\n\nWritten by Jane Doe.\n\nAgenda item one."
    chunks = fallback_text_chunks(text, max_tokens=64)
    joined = " ".join(chunk.text for chunk in chunks)
    assert "Jane Doe" in joined
    assert "Title of the minutes" in joined


def test_fallback_text_chunks_empty() -> None:
    assert fallback_text_chunks("   ", max_tokens=64) == []
