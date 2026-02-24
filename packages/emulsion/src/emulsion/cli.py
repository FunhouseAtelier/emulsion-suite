"""
Emulsion CLI — entry point for the `emulsion` command.

Commands:
  emulsion dev    Start the development server (FastAPI + Vite HMR)
  emulsion build  Build island bundles for production
  emulsion routes Output React Router-compatible route config as JSON
  emulsion new    Scaffold a new Emulsion application
"""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
from pathlib import Path
from typing import Optional

import typer

cli = typer.Typer(
    name="emulsion",
    help="Emulsion — Python-first web framework fusing FastAPI with React islands.",
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# emulsion dev
# ---------------------------------------------------------------------------

@cli.command()
def dev(
    app: str = typer.Argument(
        "main:app",
        help="Module path to the EmulsionApp instance (e.g. main:app).",
    ),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host."),
    port: int = typer.Option(8000, "--port", "-p", help="FastAPI port."),
    vite_port: int = typer.Option(5173, "--vite-port", help="Vite dev server port."),
    reload_dir: Optional[list[str]] = typer.Option(  # noqa: UP007
        None, "--reload-dir", help="Extra directories to watch for reload."
    ),
) -> None:
    """Start the development server (FastAPI + Vite HMR)."""
    from .dev import run_dev_server

    asyncio.run(
        run_dev_server(
            app,
            host=host,
            port=port,
            vite_port=vite_port,
            reload_dirs=reload_dir or ["."],
        )
    )


# ---------------------------------------------------------------------------
# emulsion build
# ---------------------------------------------------------------------------

@cli.command()
def build(
    output: str = typer.Option("static", "--output", "-o", help="Output directory."),
) -> None:
    """Build island bundles for production (runs Vite)."""
    from .build import run_build

    code = asyncio.run(run_build(output_dir=output))
    raise SystemExit(code)


# ---------------------------------------------------------------------------
# emulsion routes
# ---------------------------------------------------------------------------

@cli.command()
def routes(
    app: str = typer.Argument("main:app", help="Module:attribute of EmulsionApp."),
    output: Optional[str] = typer.Option(  # noqa: UP007
        None, "--output", "-o", help="Write JSON to file instead of stdout."
    ),
) -> None:
    """
    Print React Router-compatible route config as JSON.

    Used by the Vite plugin at build time to generate client-side routes.
    """
    emulsion_app = _load_app(app)
    data = json.dumps(emulsion_app.client_routes(), indent=2)

    if output:
        Path(output).write_text(data, encoding="utf-8")
        typer.echo(f"Routes written to {output}")
    else:
        typer.echo(data)


# ---------------------------------------------------------------------------
# emulsion new
# ---------------------------------------------------------------------------

@cli.command()
def new(
    name: str = typer.Argument(..., help="Name of the new application."),
) -> None:
    """Scaffold a new Emulsion application."""
    _scaffold_app(name)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_app(module_attr: str):
    """Import and return an EmulsionApp instance from a module:attribute string."""
    parts = module_attr.split(":")
    if len(parts) != 2:  # noqa: PLR2004
        typer.echo(f"Error: app must be in 'module:attr' format, got '{module_attr}'", err=True)
        raise SystemExit(1)

    module_name, attr_name = parts

    # Ensure the current directory is on the path so local modules are importable
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        typer.echo(f"Error: could not import module '{module_name}': {exc}", err=True)
        raise SystemExit(1) from exc

    try:
        return getattr(module, attr_name)
    except AttributeError:
        typer.echo(
            f"Error: module '{module_name}' has no attribute '{attr_name}'", err=True
        )
        raise SystemExit(1)


def _scaffold_app(name: str) -> None:
    """Create a minimal Emulsion app directory structure."""
    app_dir = Path(name)
    if app_dir.exists():
        typer.echo(f"Error: directory '{name}' already exists.", err=True)
        raise SystemExit(1)

    (app_dir / "templates").mkdir(parents=True)
    (app_dir / "islands").mkdir()
    (app_dir / "static").mkdir()

    (app_dir / "main.py").write_text(
        'from emulsion import EmulsionApp, EmulsionPage\n\n'
        'app = EmulsionApp()\n\n\n'
        '@app.page("/")\n'
        'class HomePage(EmulsionPage):\n'
        '    template = "home.html"\n'
        '    title = "Home"\n\n'
        '    async def data(self) -> dict:\n'
        '        return {"greeting": "Hello from Emulsion!"}\n',
        encoding="utf-8",
    )

    (app_dir / "templates" / "base.html").write_text(
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '  <title>{% block title %}{{ page_title }}{% endblock %}</title>\n'
        '  {{ vite_scripts() }}\n'
        '</head>\n'
        '<body>\n'
        '  <main>{% block content %}{% endblock %}</main>\n'
        '</body>\n'
        '</html>\n',
        encoding="utf-8",
    )

    (app_dir / "templates" / "home.html").write_text(
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '  <h1>{{ greeting }}</h1>\n'
        '  {{ island("Counter", {"initialCount": 0}) }}\n'
        '{% endblock %}\n',
        encoding="utf-8",
    )

    (app_dir / "islands" / "Counter.tsx").write_text(
        'import { useState } from "react";\n\n'
        'interface CounterProps {\n'
        '  initialCount: number;\n'
        '}\n\n'
        'export default function Counter({ initialCount }: CounterProps) {\n'
        '  const [count, setCount] = useState(initialCount);\n'
        '  return (\n'
        '    <div>\n'
        '      <p>Count: {count}</p>\n'
        '      <button onClick={() => setCount(c => c + 1)}>+</button>\n'
        '    </div>\n'
        '  );\n'
        '}\n',
        encoding="utf-8",
    )

    (app_dir / "vite.config.ts").write_text(
        'import { defineConfig } from "vite";\n'
        'import react from "@vitejs/plugin-react";\n'
        'import { emulsion } from "@emulsion/react/vite-plugin";\n\n'
        'export default defineConfig({\n'
        '  plugins: [\n'
        '    react(),\n'
        '    emulsion({\n'
        '      islandsDir: "./islands",\n'
        '      hydrationEntry: "./src/main.ts",\n'
        '    }),\n'
        '  ],\n'
        '  build: {\n'
        '    manifest: true,\n'
        '    rollupOptions: {\n'
        '      output: {\n'
        '        dir: "static",\n'
        '        entryFileNames: "islands/[name]-[hash].js",\n'
        '        chunkFileNames: "islands/chunks/[name]-[hash].js",\n'
        '        assetFileNames: "assets/[name]-[hash][extname]",\n'
        '      },\n'
        '    },\n'
        '  },\n'
        '});\n',
        encoding="utf-8",
    )

    (app_dir / "package.json").write_text(
        json.dumps(
            {
                "name": name,
                "private": True,
                "type": "module",
                "scripts": {
                    "dev": "emulsion dev main:app",
                    "build": "emulsion build",
                },
                "dependencies": {
                    "@emulsion/react": "workspace:*",
                    "react": "^19.0.0",
                    "react-dom": "^19.0.0",
                    "react-router": "^7.0.0",
                },
                "devDependencies": {
                    "@types/react": "^19.0.0",
                    "@types/react-dom": "^19.0.0",
                    "@vitejs/plugin-react": "^4.0.0",
                    "typescript": "^5.5.0",
                    "vite": "^6.0.0",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    typer.echo(f"✓ Created Emulsion app at ./{name}/")
    typer.echo(f"  cd {name}")
    typer.echo("  pnpm install")
    typer.echo("  uv pip install -e ../packages/emulsion")
    typer.echo("  emulsion dev")


if __name__ == "__main__":
    cli()
