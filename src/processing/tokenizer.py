from typing import Self

from tiktoken import Encoding, get_encoding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase


class OpenAITokenizerWrapper(PreTrainedTokenizerBase):
    """tiktoken wrapper that satisfies Docling HybridChunker's tokenizer protocol."""

    def __init__(self, model_name: str = "cl100k_base", max_length: int = 8191, **kwargs) -> None:
        super().__init__(model_max_length=max_length, **kwargs)
        self.tokenizer: Encoding = get_encoding(encoding_name=model_name)
        self._vocab_size: int = self.tokenizer.max_token_value

    def encode(
        self,
        text: str,
        text_pair: str | None = None,
        add_special_tokens: bool = False,
        **kwargs: object,
    ) -> list[int]:
        """Return tiktoken ids. HybridChunker/semchunk call this with add_special_tokens."""
        payload = text if text_pair is None else f"{text} {text_pair}"
        return self.tokenizer.encode(text=payload)

    def tokenize(
        self, text: str, pair: str | None = None, add_special_tokens: bool = True, **kwargs
    ) -> list[str]:
        return [str(token) for token in self.encode(text=text, text_pair=pair)]

    def _tokenize(self, text: str) -> list[str]:
        return self.tokenize(text=text)

    def _convert_token_to_id(self, token: str) -> int:
        return int(token)

    def _convert_id_to_token(self, index: int) -> str:
        return str(index)

    def get_vocab(self) -> dict[str, int]:
        return {str(key): value for key, value in enumerate(range(self.vocab_size))}

    @property
    def vocab_size(self) -> int:
        return self._vocab_size

    def save_vocabulary(
        self,
        save_directory: str | None = None,
        filename_prefix: str | None = None,
    ) -> tuple[str]:
        return (save_directory or "",)

    @classmethod
    def from_pretrained(cls, *args, **kwargs) -> Self:
        return cls()
