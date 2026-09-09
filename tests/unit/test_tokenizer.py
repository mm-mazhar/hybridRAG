import semchunk

from processing.tokenizer import OpenAITokenizerWrapper


def test_encode_accepts_add_special_tokens() -> None:
    tokenizer = OpenAITokenizerWrapper(max_length=64)
    tokens = tokenizer.encode("hello world", add_special_tokens=False)
    assert isinstance(tokens, list)
    assert tokens
    assert all(isinstance(token, int) for token in tokens)


def test_encode_length_matches_tokenize() -> None:
    tokenizer = OpenAITokenizerWrapper(max_length=128)
    text = "Board of Elementary and Secondary Education " * 40
    encoded = tokenizer.encode(text, add_special_tokens=False)
    assert len(encoded) == len(tokenizer.tokenize(text))


def test_semchunk_splits_with_wrapper() -> None:
    tokenizer = OpenAITokenizerWrapper(max_length=128)
    splitter = semchunk.chunkerify(tokenizer, chunk_size=32)
    parts = splitter.chunk("word " * 400)
    assert len(parts) > 1
