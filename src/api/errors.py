from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import APIStatusError, AuthenticationError, RateLimitError

_AUTH_DETAIL = (
    "The embedding provider rejected the API key. Use an OpenRouter key (sk-or-...) "
    "with openrouter.ai, or an OpenAI key (sk-...) with api.openai.com."
)


def register_exception_handlers(app: FastAPI) -> None:
    """Map provider SDK errors to JSON `{detail}` bodies the UI can show."""

    @app.exception_handler(AuthenticationError)
    async def _auth_error(_request: Request, _exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": _AUTH_DETAIL})

    @app.exception_handler(RateLimitError)
    async def _rate_error(_request: Request, _exc: RateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "The embedding provider rate-limited the request."},
        )

    @app.exception_handler(APIStatusError)
    async def _api_error(_request: Request, exc: APIStatusError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": provider_error_detail(exc.body)})


def provider_error_detail(body: object) -> str:
    """Pull a safe message out of an OpenAI-compatible error body."""
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message
    return "The embedding provider request failed."
