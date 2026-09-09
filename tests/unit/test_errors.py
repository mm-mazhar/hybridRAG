from api.errors import provider_error_detail


def test_provider_error_detail_reads_message() -> None:
    assert provider_error_detail({"error": {"message": "model not found"}}) == "model not found"


def test_provider_error_detail_fallback() -> None:
    assert provider_error_detail(None) == "The embedding provider request failed."
