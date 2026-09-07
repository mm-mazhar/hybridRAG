from typing import Self

from tiktoken import Encoding, get_encoding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase


# Create a wrapper class to make OpenAI's tokenizer compatible with the HybridChunker interface
class OpenAITokenizerWrapper(PreTrainedTokenizerBase):
    """Minimal wrapper for OpenAI's tokenizer."""

    def __init__(self, model_name: str = "cl100k_base", max_length: int = 8191, **kwargs) -> None:
        """Initialize the tokenizer.

        Args:
            model_name: The name of the OpenAI encoding to use
            max_length: Maximum sequence length
        """
        super().__init__(model_max_length=max_length, **kwargs)
        self.tokenizer: Encoding = get_encoding(encoding_name=model_name)
        self._vocab_size: int = self.tokenizer.max_token_value

    def tokenize(
        self, text: str, pair: str | None = None, add_special_tokens: bool = True, **kwargs
    ) -> list[str]:
        """Main method used by HybridChunker."""
        return [str(object=t) for t in self.tokenizer.encode(text=text)]

    def _tokenize(self, text: str) -> list[str]:
        return self.tokenize(text=text)

    def _convert_token_to_id(self, token: str) -> int:
        return int(token)

    def _convert_id_to_token(self, index: int) -> str:
        return str(object=index)

    def get_vocab(self) -> dict[str, int]:
        return {str(object=k): v for k, v in enumerate(iterable=range(self.vocab_size))}

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
        """Class method to match HuggingFace's interface."""
        return cls()
