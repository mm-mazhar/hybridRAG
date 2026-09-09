from openai import OpenAI

from core.settings import AppSettings


def create_openai_client(*, api_key: str, base_url: str, settings: AppSettings) -> OpenAI:
    """Build an OpenAI SDK client pointed at any compatible base URL."""
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": settings.app.http_referer,
            "X-OpenRouter-Title": settings.app.title,
        },
    )


def create_chat_client(settings: AppSettings) -> OpenAI:
    """Client for chat completions (OpenRouter, OpenAI, vLLM, ...)."""
    return create_openai_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm.base_url,
        settings=settings,
    )


def create_embedding_client(settings: AppSettings) -> OpenAI:
    """Client for embeddings; may share the chat base URL or differ in YAML."""
    return create_openai_client(
        api_key=settings.llm_api_key,
        base_url=settings.embeddings.base_url,
        settings=settings,
    )
