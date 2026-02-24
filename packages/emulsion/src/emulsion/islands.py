"""
Island injection and manifest loading.

Provides:
- island() — Jinja2 global that emits a hydration placeholder <div>
- IslandManifest — loads island-manifest.json produced by @emulsion/vite-plugin
- Asset URL helpers for dev (Vite HMR) vs prod (hashed filenames)
"""

from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Jinja2 global: island()
# ---------------------------------------------------------------------------

def island(name: str, props: dict[str, Any] | None = None, *, priority: str = "eager") -> str:
    """
    Emit an island placeholder div for client-side hydration.

    Args:
        name:     The registered island component name (e.g. "AddToCart").
        props:    Props to serialise and pass to the React component.
        priority: Hydration priority — "eager" | "visible" | "idle" | "interaction".

    Returns:
        An HTML string (must be marked safe in Jinja2 with | safe).

    Example (Jinja2 template):
        {{ island("AddToCart", {"productId": product.id}) | safe }}
    """
    serialised = html.escape(json.dumps(props or {}), quote=True)
    return (
        f'<div data-island="{html.escape(name)}" '
        f'data-props="{serialised}" '
        f'data-island-priority="{html.escape(priority)}" '
        f'data-hydrated="false">'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Island manifest (loaded from island-manifest.json at startup)
# ---------------------------------------------------------------------------

@dataclass
class IslandChunk:
    file: str
    css: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


@dataclass
class IslandManifest:
    hydration_entry: IslandChunk
    islands: dict[str, IslandChunk]
    shared_chunks: dict[str, str] = field(default_factory=dict)
    version: int = 1

    @classmethod
    def load(cls, path: Path) -> "IslandManifest":
        """Load and parse island-manifest.json produced by the Vite build."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            version=data.get("version", 1),
            hydration_entry=IslandChunk(**data["hydrationEntry"]),
            islands={k: IslandChunk(**v) for k, v in data.get("islands", {}).items()},
            shared_chunks=data.get("sharedChunks", {}),
        )

    def hydration_script_tag(self, static_url_prefix: str = "/static") -> str:
        """Return the <script> tag for the hydration entry bundle."""
        src = f"{static_url_prefix}/{self.hydration_entry.file}"
        css_tags = "".join(
            f'<link rel="stylesheet" href="{static_url_prefix}/{css}">\n'
            for css in self.hydration_entry.css
        )
        return f'{css_tags}<script type="module" src="{src}"></script>'


# ---------------------------------------------------------------------------
# Dev vs. prod asset URL helpers
# ---------------------------------------------------------------------------

def is_dev_mode() -> bool:
    return os.environ.get("EMULSION_DEV_MODE", "false").lower() == "true"


def get_vite_port() -> int:
    return int(os.environ.get("EMULSION_VITE_PORT", "5173"))


def vite_scripts_html(manifest: IslandManifest | None, *, static_url_prefix: str = "/static") -> str:
    """
    Returns the HTML to inject into <head> for loading island bundles.
    - Dev:  Vite HMR client + main entry via Vite dev server
    - Prod: Hashed script + CSS tags from the island manifest
    """
    if is_dev_mode():
        port = get_vite_port()
        return (
            f'<script type="module" src="http://localhost:{port}/@vite/client"></script>\n'
            f'<script type="module" src="http://localhost:{port}/src/main.ts"></script>'
        )
    if manifest is None:
        return "<!-- emulsion: no island manifest found; run `emulsion build` -->"
    return manifest.hydration_script_tag(static_url_prefix)
