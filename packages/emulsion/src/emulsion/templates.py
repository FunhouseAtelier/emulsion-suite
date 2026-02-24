"""
Jinja2 environment factory and template response helper.

Creates an Environment pre-loaded with Emulsion's built-in globals:
  - island()           → emit island placeholder divs
  - vite_scripts()     → inject Vite HMR (dev) or hashed bundles (prod)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from starlette.templating import Jinja2Templates

from .islands import IslandManifest, island, vite_scripts_html

if TYPE_CHECKING:
    pass


def create_jinja_environment(
    template_dir: str | Path,
    manifest: IslandManifest | None = None,
    debug: bool = False,
    static_url_prefix: str = "/static",
) -> Environment:
    """
    Create a Jinja2 Environment configured for Emulsion.

    Registers:
      - island(name, props, priority)  → HTML placeholder (must use | safe)
      - vite_scripts()                 → <script>/<link> tags for islands
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "htm", "xml"]),
        auto_reload=debug,
    )

    # island() global — wraps output in Markup so callers can skip | safe
    env.globals["island"] = lambda name, props=None, priority="eager": Markup(
        island(name, props, priority=priority)
    )

    # vite_scripts() global — inject bundle tags into <head>
    env.globals["vite_scripts"] = lambda: Markup(
        vite_scripts_html(manifest, static_url_prefix=static_url_prefix)
    )

    return env


class EmulsionTemplates:
    """
    Thin wrapper around Starlette's Jinja2Templates that accepts a
    pre-configured Jinja2 Environment (so Emulsion globals are available).
    """

    def __init__(self, env: Environment) -> None:
        self._templates = Jinja2Templates(env=env)

    def TemplateResponse(
        self,
        name: str,
        context: dict[str, Any],
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
    ):
        return self._templates.TemplateResponse(
            name=name,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )
