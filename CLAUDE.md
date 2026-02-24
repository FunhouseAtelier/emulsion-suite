# Emulsion Suite — Project Guide

## What This Is

**Emulsion** is a Python-first web application framework that fuses FastAPI with React. It serves HTML pages via FastAPI/Jinja2 and embeds React "islands" anywhere in those pages for interactive content. Think Next.js/Remix, but Python-native.

**Repository**: `FunhouseAtelier/emulsion-suite` (public monorepo)
**Owner**: Jason at Funhouse Atelier

## Architecture Decisions

- **React Router v7 Mode**: `createBrowserRouter` (Data Mode within Library Mode)
  - FastAPI owns all server routing and initial page loads
  - React Router owns client-side SPA transitions via loaders that fetch `?format=json` from FastAPI
  - A custom `@emulsion/vite-plugin` handles island bundling (not Framework Mode)
- **Runtime**: Python-only production server (FastAPI/uvicorn). Node.js is build-time only (Vite).
- **Islands**: React components injected into Jinja2 templates via `{{ island("Name", {props}) }}` placeholders, hydrated client-side with priority scheduling (eager/visible/idle/interaction)
- **Route fusion**: A single `@app.page("/path")` Python decorator generates both a FastAPI HTTP handler and a React Router client-side route

## Package Structure

```
emulsion-suite/                     # pnpm workspace monorepo
├── packages/
│   ├── emulsion/                   # Python core — FastAPI integration, Jinja2, CLI, extensions
│   └── emulsion-react/             # TypeScript — @emulsion/react (hydration, Island component, Vite plugin)
├── extensions/
│   ├── emulsion-siteswan/          # SiteSwan website importer (Python, stub)
│   └── emulsion-export/            # Template exporter (Python, stub)
├── apps/
│   └── example-app/                # Reference app with Counter, AddToCart, ReviewCarousel islands
```

## Key Conventions

- **Python**: src/ layout, hatchling build, pyproject.toml config, Python >=3.11
- **TypeScript**: ESM only, React 19, React Router 7, Vite 6, TypeScript 5
- **Monorepo**: pnpm workspaces; `workspace:*` protocol for local package references
- **Islands**: Default exports from `.tsx`/`.jsx` files in an `islands/` directory. Filename stem = island name.
- **Vite plugin**: Auto-generates island registry and `island-manifest.json` at build time
- **CLI**: `emulsion dev` (concurrent FastAPI + Vite), `emulsion build`, `emulsion routes`, `emulsion new`
- **Extensions**: Subclass `EmulsionExtension` with lifecycle hooks (on_app_created, on_fastapi_ready, etc.)

## Technology Stack

| Layer | Technology |
|---|---|
| Python server | FastAPI >=0.115, uvicorn, Jinja2, Pydantic v2 |
| Python tooling | hatchling, uv, typer, ruff, mypy, pytest |
| JS bundler | Vite >=6.0 |
| UI | React 19, React Router 7 (createBrowserRouter) |
| Monorepo | pnpm 9, changesets |

## Development Workflow

```bash
# JS dependencies (from repo root)
pnpm install

# Python package (in a virtualenv)
uv pip install -e packages/emulsion

# Start dev server (from apps/example-app/)
emulsion dev
```

## User Preferences

- Thorough explanations of unfamiliar tooling (pnpm, monorepo patterns, Python packaging)
- Prefers reviewing architecture decisions before implementation
- `.env.example` files are tracked in git; actual `.env` files are not
- Primary development OS: Ubuntu Studio 24
