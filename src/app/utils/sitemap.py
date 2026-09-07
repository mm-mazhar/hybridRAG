# """
# sitemap.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# """

import xml.etree.ElementTree as ET
from typing import Literal
from urllib.parse import urljoin

import requests


def get_sitemap_urls(base_url: str, sitemap_filename: str = "sitemap.xml") -> list[str]:
    """Fetches and parses a sitemap XML file to extract URLs.

    Args:
        base_url: The base URL of the website
        sitemap_filename: The filename of the sitemap (default: sitemap.xml)

    Returns:
        List of URLs found in the sitemap. If sitemap is not found, returns a list
        containing only the base URL.

    Raises:
        ValueError: If there's an error fetching (except 404) or parsing the sitemap
    """
    try:
        sitemap_url: str = urljoin(base=base_url, url=sitemap_filename)

        # Check if sitemap exists first
        head_response: requests.Response = requests.head(
            url=sitemap_url, timeout=10, allow_redirects=True
        )

        # Return just the base URL if sitemap doesn't exist
        if head_response.status_code != 200:
            return [base_url.rstrip("/")]

        # Fetch sitemap content only if it exists
        response: requests.Response = requests.get(url=sitemap_url, timeout=10)
        response.raise_for_status()

        # Parse XML content
        root: ET.Element = ET.fromstring(text=response.content)

        # Handle different XML namespaces that sitemaps might use
        namespaces: dict[str, str] | Literal[""] = (
            {"ns": root.tag.split(sep="}")[0].strip("{")} if "}" in root.tag else ""
        )

        # Extract URLs using namespace if present
        if namespaces:
            urls: list[str | None] = [
                elem.text for elem in root.findall(path=".//ns:loc", namespaces=namespaces)
            ]
        else:
            urls = [elem.text for elem in root.findall(path=".//loc")]

        # Filter out None values and return only valid URLs
        return [url for url in urls if url is not None]

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch sitemap: {str(object=e)}") from e
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse sitemap XML: {str(object=e)}") from e
    except Exception as e:
        raise ValueError(f"Unexpected error processing sitemap: {str(object=e)}") from e


# if __name__ == "__main__":
#     print(get_sitemap_urls(base_url="https://ds4sd.github.io/docling/"))
