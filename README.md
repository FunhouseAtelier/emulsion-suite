# Emulsion Suite

A Python-first, UI-agnostic web application framework built on FastAPI. Serve HTML pages via Jinja2 templates and embed interactive "islands" powered by React, Vue, Svelte, or any JS UI library.

Think Next.js/Remix, but Python-native — or Astro, but with Python owning the server.

## Key Ideas

- **Python owns the server.** Routing, data loading, templates, and middleware are all FastAPI. Node.js is build-time only.
- **Islands architecture.** Interactive components are opt-in "islands" hydrated into server-rendered HTML, keeping pages fast by default.
- **UI-agnostic core.** The `emulsion` package has zero JS framework opinions. UI integration is provided by adapter packages — `emulsion-react` today, with `emulsion-vue`, `emulsion-svelte`, etc. planned.
- **Route fusion.** A single `@app.page("/path")` Python decorator generates both a FastAPI server route and a React Router client-side route.

## Packages

| Package | Description | Version |
|---|---|---|
| [`emulsion`](packages/emulsion/) | Python core — FastAPI integration, Jinja2, CLI, extensions | 0.1.0 |
| [`@emulsion/react`](packages/emulsion-react/) | UI adapter — island hydration, Vite plugin, React Router integration | 0.1.0 |

### Extensions (stubs)

| Package | Description |
|---|---|
| [`emulsion-siteswan`](extensions/emulsion-siteswan/) | SiteSwan website importer |
| [`emulsion-export`](extensions/emulsion-export/) | Template exporter |

## Quick Start

```bash
# Clone and install JS dependencies
git clone https://github.com/FunhouseAtelier/emulsion-suite.git
cd emulsion-suite
pnpm install

# Build the React adapter
pnpm --filter @emulsion/react build

# Create a Python virtual environment and install the core package
uv venv
source .venv/bin/activate
uv pip install -e packages/emulsion

# Run the example app
cd apps/example-app
emulsion dev
```

Open http://localhost:8000 to see the app. FastAPI serves the pages; Vite provides HMR for island development.

## Example

```python
# main.py
from emulsion import EmulsionApp, EmulsionPage

app = EmulsionApp()

@app.page("/")
class HomePage(EmulsionPage):
    template = "home.html"

    async def data(self) -> dict:
        return {"greeting": "Hello from Emulsion!"}
```

```html
<!-- templates/home.html -->
{% extends "base.html" %}
{% block content %}
  <h1>{{ greeting }}</h1>
  {{ island("Counter", {"initialCount": 0}) }}
{% endblock %}
```

```tsx
// islands/Counter.tsx
import { useState } from "react";

export default function Counter({ initialCount }: { initialCount: number }) {
  const [count, setCount] = useState(initialCount);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount((c) => c + 1)}>+</button>
      <button onClick={() => setCount((c) => c - 1)}>−</button>
      <button onClick={() => setCount(initialCount)}>Reset</button>
    </div>
  );
}
```

## How It Works

1. **FastAPI** handles all HTTP requests and renders Jinja2 templates with `{{ island("Name", {props}) }}` placeholders.
2. **Vite** bundles each island component as a separate chunk with a custom `@emulsion/vite-plugin`.
3. **On page load**, the hydration runtime scans for `[data-island]` placeholder divs, lazy-loads their JS chunks, and mounts React roots with priority scheduling (`eager`, `visible`, `idle`, `interaction`).
4. **SPA navigation** (when configured) uses React Router's `createBrowserRouter` with loaders that fetch `?format=json` from FastAPI, enabling client-side page transitions without full reloads.

## CLI

```bash
emulsion dev [main:app]    # Start FastAPI + Vite dev servers concurrently
emulsion build             # Build island bundles for production
emulsion routes [main:app] # Output React Router route config as JSON
emulsion new <name>        # Scaffold a new Emulsion app
```

## Technology Stack

| Layer | Technology |
|---|---|
| Python server | FastAPI, uvicorn, Jinja2, Pydantic v2 |
| Python tooling | hatchling, uv, typer, ruff, mypy, pytest |
| JS bundler | Vite 6 |
| UI (via adapter) | React 19, React Router 7 |
| Monorepo | pnpm 9, changesets |

## Repository Structure

```
emulsion-suite/
├── packages/
│   ├── emulsion/            # Python core (UI-agnostic)
│   └── emulsion-react/      # React UI adapter
├── extensions/
│   ├── emulsion-siteswan/   # SiteSwan importer (stub)
│   └── emulsion-export/     # Template exporter (stub)
└── apps/
    └── example-app/         # Reference app with Counter, AddToCart, ReviewCarousel islands
```

## Development

```bash
# JS dependencies (from repo root)
pnpm install

# Python core (in a virtualenv)
uv pip install -e packages/emulsion

# Build the React adapter (required once, or after changes)
pnpm --filter @emulsion/react build

# Run the example app
cd apps/example-app
emulsion dev
```

## License

MIT
