"""
SiteSwanExtension — Emulsion extension for importing SiteSwan websites.

Registers admin routes under /admin/siteswan/ for triggering imports,
checking status, and browsing imported pages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from emulsion.extensions import EmulsionExtension
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .importer import SiteSwanImporter

if TYPE_CHECKING:
    from emulsion.app import EmulsionApp
    from fastapi import FastAPI
    from jinja2 import Environment


class SiteSwanExtension(EmulsionExtension):
    """
    Imports a SiteSwan website into an Emulsion project.

    Args:
        site_id:  SiteSwan site identifier.
        api_key:  SiteSwan API key (optional; some operations are public).
        prefix:   URL prefix for admin routes. Default: "/admin/siteswan".
    """

    name = "siteswan"
    version = "0.1.0"

    def __init__(
        self,
        site_id: str,
        api_key: str = "",
        prefix: str = "/admin/siteswan",
    ) -> None:
        self.site_id = site_id
        self.api_key = api_key
        self.prefix = prefix
        self._importer = SiteSwanImporter(site_id=site_id, api_key=api_key)

    def on_app_created(self, app: "EmulsionApp") -> None:
        """Register SiteSwan admin routes with the FastAPI application."""
        router = APIRouter(prefix=self.prefix, tags=["siteswan"])

        @router.get("/status")
        async def import_status() -> JSONResponse:
            """Return the current import status."""
            return JSONResponse({"site_id": self.site_id, "status": "ready"})

        @router.post("/import")
        async def trigger_import() -> JSONResponse:
            """Trigger a fresh import of the SiteSwan site."""
            result = await self._importer.run()
            return JSONResponse(result)

        @router.get("/pages")
        async def list_pages() -> JSONResponse:
            """List pages discovered in the last import."""
            pages = await self._importer.list_pages()
            return JSONResponse({"pages": pages})

        app.fastapi.include_router(router)

    def on_jinja_env_created(self, env: "Environment") -> None:
        """Add SiteSwan-specific Jinja2 filters."""
        env.filters["siteswan_asset"] = self._asset_url

    def _asset_url(self, path: str) -> str:
        """Convert a SiteSwan asset path to its CDN URL."""
        return f"https://cdn.siteswan.com/{self.site_id}/{path.lstrip('/')}"
