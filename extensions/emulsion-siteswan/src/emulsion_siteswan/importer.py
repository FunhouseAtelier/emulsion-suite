"""
SiteSwanImporter — downloads and converts a SiteSwan site.

This is a stub implementation. A full implementation would:
1. Authenticate with the SiteSwan API
2. Enumerate pages, assets, and data
3. Convert SiteSwan HTML structure to Jinja2 templates
4. Map SiteSwan widgets to Emulsion islands
5. Download and localise assets
"""

from __future__ import annotations

import httpx


class SiteSwanImporter:
    """
    Downloads and converts a SiteSwan website to Emulsion format.

    Args:
        site_id:  SiteSwan site identifier.
        api_key:  SiteSwan API key.
    """

    SITESWAN_BASE_URL = "https://api.siteswan.com/v1"

    def __init__(self, site_id: str, api_key: str = "") -> None:
        self.site_id = site_id
        self.api_key = api_key

    async def run(self) -> dict:
        """
        Execute a full site import.

        Returns a summary dict with counts of imported pages and assets.
        """
        pages = await self.list_pages()
        # TODO: for each page, call _convert_page() and write Jinja2 template
        return {
            "status": "ok",
            "site_id": self.site_id,
            "pages_discovered": len(pages),
            "pages_converted": 0,  # stub
        }

    async def list_pages(self) -> list[dict]:
        """
        Return a list of pages in the SiteSwan site.

        Stub: returns an empty list until SiteSwan API is integrated.
        """
        # Real implementation:
        # async with httpx.AsyncClient() as client:
        #     resp = await client.get(
        #         f"{self.SITESWAN_BASE_URL}/sites/{self.site_id}/pages",
        #         headers={"Authorization": f"Bearer {self.api_key}"},
        #     )
        #     resp.raise_for_status()
        #     return resp.json()["pages"]
        return []

    async def _convert_page(self, page: dict) -> str:
        """
        Convert a SiteSwan page dict to a Jinja2 template string.

        Stub implementation.
        """
        title = page.get("title", "Untitled")
        return (
            '{{% extends "base.html" %}}\n'
            '{{% block content %}}\n'
            f"<h1>{title}</h1>\n"
            "{{% endblock %}}\n"
        )
