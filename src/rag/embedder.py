from typing import Protocol

from openai import OpenAI

from core.settings import AppSettings


class QueryEmbedder(Protocol):
    """Anything that can embed a search query (production Embedder or test doubles)."""

    def embed_query(self, query: str) -> list[float]: ...


class Embedder:
    """OpenAI-compatible embeddings client used for index and query vectors."""

    def __init__(self, client: OpenAI, model: str, batch_size: int = 64) -> None:
        self._client = client
        self._model = model
        self._batch_size = max(1, batch_size)

    @classmethod
    def from_settings(cls, settings: AppSettings, client: OpenAI) -> "Embedder":
        return cls(
            client=client,
            model=settings.embeddings.model,
            batch_size=settings.embeddings.batch_size,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed texts in batches. Empty input returns an empty list."""
        if not texts:
            return []
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            response = self._client.embeddings.create(model=self._model, input=batch)
            ordered = sorted(response.data, key=lambda item: item.index)
            vectors.extend(item.embedding for item in ordered)
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embedding count mismatch: expected {len(texts)}, got {len(vectors)}"
            )
        return vectors

    def embed_query(self, query: str) -> list[float]:
        """Embed a single search query."""
        vectors = self.embed_texts([query])
        return vectors[0]
