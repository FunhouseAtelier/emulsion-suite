"""
Extension API base class.

Extensions hook into the Emulsion application lifecycle to add routes,
middleware, Jinja2 filters, islands, and other capabilities.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from jinja2 import Environment

    from .app import EmulsionApp


class EmulsionExtension(ABC):
    """
    Base class for all Emulsion extensions.

    Subclass this and pass instances to EmulsionApp(extensions=[...]).
    Methods are called in order during application startup.
    """

    name: str = "unnamed"
    version: str = "0.0.1"

    def on_app_created(self, app: "EmulsionApp") -> None:
        """
        Called when EmulsionApp is instantiated.
        Register routes, middleware, or perform early setup here.
        """

    def on_fastapi_ready(self, fastapi_app: "FastAPI") -> None:
        """
        Called after FastAPI is fully configured.
        Mount sub-applications or add final middleware here.
        """

    def on_jinja_env_created(self, env: "Environment") -> None:
        """
        Extend the Jinja2 environment.
        Add custom filters, globals, or extensions here.
        """

    def on_island_registry(self, registry: dict[str, str]) -> dict[str, str]:
        """
        Called at build time with the island name→file-path registry.
        Extensions can inject their own islands (e.g., from a UI kit).
        Returns the (possibly modified) registry.
        """
        return registry

    def on_build_complete(self, manifest_path: str) -> None:
        """
        Called after the Vite build completes.
        Extensions can post-process built assets here.
        """

    def on_shutdown(self) -> None:
        """Called when the application shuts down. Release resources here."""
