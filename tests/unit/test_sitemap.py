from pytest import MonkeyPatch

from processing.sitemap import absolute_sitemap_url, get_sitemap_urls


class _FakeResponse:
    def __init__(
        self,
        content: bytes,
        status_code: int = 200,
        content_type: str = "application/xml",
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}


def test_absolute_sitemap_url_keeps_path() -> None:
    assert (
        absolute_sitemap_url("https://github.com/zernio-dev/zernflow", "sitemap.xml")
        == "https://github.com/zernio-dev/zernflow/sitemap.xml"
    )


def test_html_sitemap_falls_back_to_origin(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "processing.sitemap.requests.get",
        lambda *_args, **_kwargs: _FakeResponse(
            b"<!DOCTYPE html><html><body>Not a sitemap</body></html>",
            content_type="text/html",
        ),
    )
    assert get_sitemap_urls("https://github.com/zernio-dev/zernflow") == [
        "https://github.com/zernio-dev/zernflow"
    ]


def test_junk_xml_falls_back_to_origin(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "processing.sitemap.requests.get",
        lambda *_args, **_kwargs: _FakeResponse(b"<root/>\n<html></html>\n"),
    )
    assert get_sitemap_urls("https://example.com/docs") == ["https://example.com/docs"]


def test_valid_urlset(monkeypatch: MonkeyPatch) -> None:
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.com/a</loc></url>
      <url><loc>https://example.com/b</loc></url>
    </urlset>
    """
    monkeypatch.setattr(
        "processing.sitemap.requests.get",
        lambda *_args, **_kwargs: _FakeResponse(xml),
    )
    assert get_sitemap_urls("https://example.com") == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_missing_sitemap_falls_back_to_origin(monkeypatch: MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    def fake_get(url: str, **_kwargs: object) -> _FakeResponse:
        seen["url"] = url
        return _FakeResponse(b"", status_code=404)

    monkeypatch.setattr("processing.sitemap.requests.get", fake_get)
    assert get_sitemap_urls("https://example.com/app") == ["https://example.com/app"]
    assert seen["url"] == "https://example.com/app/sitemap.xml"
