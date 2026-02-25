"""
Route registration system.

Converts @app.page() decorated EmulsionPage classes into FastAPI route handlers.
Also exports a React Router-compatible route manifest for SPA client-side navigation.
"""

from __future__ import annotations

import re
from typing import Any, Type, TYPE_CHECKING

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

if TYPE_CHECKING:
    from .app import EmulsionApp
    from .page import EmulsionPage
    from .templates import EmulsionTemplates


_JSON_ACCEPT = "application/json"


class RouteRegistry:
    """
    Manages all registered EmulsionPage routes.

    For each registered page:
    - Adds a FastAPI route that renders HTML or JSON depending on the request
    - Stores metadata for React Router client-route generation
    """

    def __init__(self) -> None:
        self._routes: list[dict[str, Any]] = []

    def register(
        self,
        app: "EmulsionApp",
        path: str,
        page_class: Type["EmulsionPage"],
        **route_kwargs: Any,
    ) -> None:
        """Register a page class as a FastAPI route handler."""
        path_params = _extract_path_params(path)
        templates = app._templates

        # Build a FastAPI-compatible async handler via closure
        handler = _build_handler(page_class, path_params, templates)

        app.fastapi.add_api_route(
            path=path,
            endpoint=handler,
            response_class=HTMLResponse,
            response_model=None,
            name=route_kwargs.pop("name", page_class.__name__),
            **route_kwargs,
        )

        self._routes.append(
            {
                "python_path": path,
                "rr_path": _python_path_to_rr(path),
                "page_class": page_class.__name__,
                "islands": list(getattr(page_class, "islands", [])),
                "data_url": path + "?format=json",
            }
        )

    def client_routes(self) -> list[dict[str, Any]]:
        """
        Return route config for React Router's createBrowserRouter.

        The Vite plugin reads this (via `emulsion routes --json`) at build time
        to generate the client-side route table that mirrors Python routes.
        """
        return [
            {
                "path": r["rr_path"],
                "islands": r["islands"],
                "dataUrl": r["data_url"],
            }
            for r in self._routes
        ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_path_params(path: str) -> list[str]:
    """Extract {param} names from a FastAPI-style path."""
    return re.findall(r"\{(\w+)\}", path)


def _python_path_to_rr(path: str) -> str:
    """Convert FastAPI path syntax to React Router syntax.

    /products/{product_id}  →  /products/:product_id
    """
    return re.sub(r"\{(\w+)\}", r":\1", path)


def _build_handler(
    page_class: Type["EmulsionPage"],
    path_params: list[str],
    templates: "EmulsionTemplates",
):
    """
    Dynamically build an async FastAPI route handler for a given EmulsionPage.

    FastAPI inspects function signatures for path parameter injection.
    We construct a handler with the correct keyword arguments via exec() so
    FastAPI's dependency injection sees the named parameters.
    """
    if not path_params:
        # No path parameters — simple handler
        async def handler(request: Request) -> HTMLResponse | JSONResponse:
            page = page_class(request)
            if _wants_json(request):
                return await page._render_json()
            return await page._render_html(templates)

        handler.__name__ = page_class.__name__ + "_handler"
        return handler

    # Build a handler whose signature includes all path parameters.
    # This is necessary so FastAPI injects them correctly.
    params_sig = ", ".join(path_params)
    params_dict = "{" + ", ".join(f'"{p}": {p}' for p in path_params) + "}"

    exec_globals: dict[str, Any] = {
        "Request": Request,
        "HTMLResponse": HTMLResponse,
        "JSONResponse": JSONResponse,
        "page_class": page_class,
        "templates": templates,
        "_wants_json": _wants_json,
    }
    exec_locals: dict[str, Any] = {}

    func_src = f"""
async def handler(request: Request, {params_sig}) -> HTMLResponse | JSONResponse:
    page = page_class(request)
    kwargs = {params_dict}
    if _wants_json(request):
        return await page._render_json(**kwargs)
    return await page._render_html(templates, **kwargs)
"""
    exec(func_src, exec_globals, exec_locals)  # noqa: S102
    fn = exec_locals["handler"]
    fn.__name__ = page_class.__name__ + "_handler"
    return fn


def _wants_json(request: Request) -> bool:
    """Return True if the client expects a JSON response."""
    accept = request.headers.get("Accept", "")
    fmt = request.query_params.get("format", "")
    return _JSON_ACCEPT in accept or fmt == "json"
