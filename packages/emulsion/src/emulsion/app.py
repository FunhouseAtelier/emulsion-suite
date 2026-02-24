"""
EmulsionApp — the central application object.

Wraps FastAPI and wires together:
  - Jinja2 template engine with island support
  - Island manifest loading
  - Route registration via @app.page()
  - Extension lifecycle management
  - Static file serving
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence, Type

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .extensions import EmulsionExtension
from .islands import IslandManifest
from .routing import RouteRegistry
from .templates import EmulsionTemplates, create_jinja_environment


class EmulsionApp:
    """
    The main Emulsion application class.

    Usage:
        app = EmulsionApp()

        @app.page("/")
        class HomePage(EmulsionPage):
            template = "home.html"

        # The FastAPI ASGI app is at app.fastapi (or app.asgi for uvicorn)
    """

    def __init__(
        self,
        *,
        title: str = "Emulsion App",
        template_dir: str | Path = "templates",
        static_dir: str | Path = "static",
        island_manifest: str | Path = "static/.vite/island-manifest.json",
        extensions: Sequence[EmulsionExtension] = (),
        debug: bool = False,
        **fastapi_kwargs: Any,
    ) -> None:
        self._debug = debug
        self._extensions = list(extensions)
        self._route_registry = RouteRegistry()

        # Resolve paths relative to caller's working directory
        self._template_dir = Path(template_dir)
        self._static_dir = Path(static_dir)

        # Create the underlying FastAPI application
        self.fastapi = FastAPI(title=title, debug=debug, **fastapi_kwargs)

        # Load island manifest (graceful failure before first `emulsion build`)
        self._manifest: IslandManifest | None = None
        manifest_path = Path(island_manifest)
        if manifest_path.exists():
            self._manifest = IslandManifest.load(manifest_path)

        # Set up Jinja2 environment with Emulsion globals
        jinja_env = create_jinja_environment(
            template_dir=self._template_dir,
            manifest=self._manifest,
            debug=debug,
        )
        self._templates = EmulsionTemplates(jinja_env)

        # Mount static files if the directory exists
        if self._static_dir.exists():
            self.fastapi.mount(
                "/static",
                StaticFiles(directory=str(self._static_dir)),
                name="static",
            )

        # Run extension lifecycle hooks
        for ext in self._extensions:
            ext.on_app_created(self)
            ext.on_jinja_env_created(jinja_env)

        for ext in self._extensions:
            ext.on_fastapi_ready(self.fastapi)

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def page(self, path: str, **route_kwargs: Any):
        """
        Decorator to register an EmulsionPage subclass as a route handler.

        @app.page("/products/{product_id}")
        class ProductPage(EmulsionPage):
            template = "product.html"
            islands = ["AddToCart"]

            async def data(self, product_id: str) -> dict:
                return {"product": await get_product(product_id)}
        """
        def decorator(page_class: Type) -> Type:
            self._route_registry.register(
                app=self,
                path=path,
                page_class=page_class,
                **route_kwargs,
            )
            return page_class

        return decorator

    # ------------------------------------------------------------------
    # ASGI interface
    # ------------------------------------------------------------------

    @property
    def asgi(self) -> FastAPI:
        """The ASGI application to pass to uvicorn."""
        return self.fastapi

    # Support `uvicorn main:app` where app is an EmulsionApp instance
    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        await self.fastapi(scope, receive, send)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def client_routes(self) -> list[dict[str, Any]]:
        """
        Return the React Router-compatible route manifest.
        Used by `emulsion routes --json` at build time.
        """
        return self._route_registry.client_routes()
