"""
EmulsionPage — base class for page handlers.

Subclass this and decorate with @app.page("/path") to register a route.
The framework calls data() for template context, then renders the template.
The same handler also serves JSON at ?format=json for React Router SPA navigation.
"""

from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

if TYPE_CHECKING:
    from .templates import EmulsionTemplates


class EmulsionPage:
    """
    Base class for Emulsion page handlers.

    Class attributes:
        template:  Jinja2 template filename (required).
        islands:   Names of React islands used on this page (for preloading hints).
        title:     HTML <title> value — injected into template context as page_title.

    Instance attributes:
        request:   The incoming FastAPI Request.

    Example:
        @app.page("/products/{product_id}")
        class ProductPage(EmulsionPage):
            template = "product.html"
            islands = ["AddToCart", "ReviewCarousel"]
            title = "Product Detail"

            async def data(self, product_id: str) -> dict:
                return {"product": await fetch_product(product_id)}
    """

    template: ClassVar[str]
    islands: ClassVar[list[str]] = []
    title: ClassVar[str] = ""

    def __init__(self, request: Request) -> None:
        self.request = request

    async def data(self, **path_params: Any) -> dict[str, Any]:
        """
        Override to return Jinja2 template context data.
        Receives path parameters as keyword arguments matching the route pattern.
        """
        return {}

    async def _render_html(self, templates: "EmulsionTemplates", **path_params: Any) -> HTMLResponse:
        """Internal: called by the route registry to render the full HTML page."""
        context = await self.data(**path_params)
        context.setdefault("request", self.request)
        context.setdefault("page_title", self.title)
        context.setdefault("page_islands", self.islands)
        return templates.TemplateResponse(self.template, context)

    async def _render_json(self, **path_params: Any) -> JSONResponse:
        """
        Internal: returns page data as JSON for React Router's SPA loader.
        Triggered when the request includes ?format=json or Accept: application/json.
        """
        data = await self.data(**path_params)
        return JSONResponse(data)
