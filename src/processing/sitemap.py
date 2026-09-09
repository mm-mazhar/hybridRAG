import logging
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests

logger = logging.getLogger(__name__)

_MAX_SITEMAP_URLS = 12
_MAX_CHILD_SITEMAPS = 5
_TIMEOUT_SECONDS = 15
_HEADERS = {"User-Agent": "hybridRAG/0.1 (local document ingest)"}


def get_sitemap_urls(base_url: str, sitemap_filename: str = "sitemap.xml") -> list[str]:
    """Return page URLs from a sitemap, or the origin if the sitemap is missing or not XML."""
    origin = base_url.rstrip("/")
    sitemap_url = absolute_sitemap_url(origin, sitemap_filename)
    try:
        response = requests.get(
            sitemap_url,
            timeout=_TIMEOUT_SECONDS,
            allow_redirects=True,
            headers=_HEADERS,
        )
    except requests.RequestException as exc:
        logger.warning("Sitemap fetch failed for %s: %s", sitemap_url, exc)
        return [origin]

    if response.status_code != 200 or not looks_like_xml(response):
        return [origin]

    try:
        found = parse_sitemap_locs(response.content, depth=0)
    except ET.ParseError as exc:
        logger.warning("Sitemap XML unusable at %s: %s", sitemap_url, exc)
        return [origin]

    unique: list[str] = []
    seen: set[str] = set()
    for raw in found:
        url = _http_url(raw)
        if url is None or url in seen:
            continue
        seen.add(url)
        unique.append(url)
        if len(unique) >= _MAX_SITEMAP_URLS:
            break
    return unique or [origin]


def absolute_sitemap_url(base_url: str, sitemap_filename: str) -> str:
    """Join sitemap.xml onto the origin without dropping the last path segment."""
    name = sitemap_filename.strip()
    if name.startswith(("http://", "https://")):
        return name
    base = base_url if base_url.endswith("/") else f"{base_url}/"
    return urljoin(base, name.lstrip("/"))


def looks_like_xml(response: requests.Response) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    if "html" in content_type and "xml" not in content_type:
        return False
    snippet = response.content.lstrip()[:400].lower()
    if snippet.startswith(b"<!doctype html") or snippet.startswith(b"<html"):
        return False
    return (
        snippet.startswith(b"<?xml")
        or snippet.startswith(b"<urlset")
        or snippet.startswith(b"<sitemapindex")
        or b"<urlset" in snippet
        or b"<sitemapindex" in snippet
    )


def parse_sitemap_locs(payload: bytes, depth: int) -> list[str]:
    """Read <loc> entries from a urlset or a one-level sitemap index."""
    root = ET.fromstring(payload)
    kind = _local_name(root.tag)
    if kind == "sitemapindex":
        if depth >= 1:
            return []
        child_sitemaps = [
            text
            for elem in root.iter()
            if _local_name(elem.tag) == "loc" and (text := (elem.text or "").strip())
        ]
        urls: list[str] = []
        for child in child_sitemaps[:_MAX_CHILD_SITEMAPS]:
            urls.extend(_locs_from_child_sitemap(child, depth=depth + 1))
            if len(urls) >= _MAX_SITEMAP_URLS:
                break
        return urls
    return [
        text
        for elem in root.iter()
        if _local_name(elem.tag) == "loc" and (text := (elem.text or "").strip())
    ]


def _locs_from_child_sitemap(url: str, depth: int) -> list[str]:
    try:
        response = requests.get(
            url,
            timeout=_TIMEOUT_SECONDS,
            headers=_HEADERS,
            allow_redirects=True,
        )
    except requests.RequestException:
        return []
    if response.status_code != 200 or not looks_like_xml(response):
        return []
    try:
        return parse_sitemap_locs(response.content, depth=depth)
    except ET.ParseError:
        return []


def _http_url(value: str) -> str | None:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return value.strip()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
