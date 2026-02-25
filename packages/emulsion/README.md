# Emulsion

A Python-first, UI-agnostic web application framework built on FastAPI. Serve HTML pages via Jinja2 templates and embed interactive "islands" powered by React, Vue, Svelte, or any JS UI library.

## Features

- **FastAPI integration** — routing, middleware, dependency injection
- **Jinja2 templates** — server-rendered HTML with island placeholders
- **Islands architecture** — interactive components hydrated client-side with priority scheduling
- **Route fusion** — `@app.page()` generates both server and client-side routes
- **UI-agnostic** — core has zero JS framework opinions; adapters like `emulsion-react` provide UI integration
- **CLI** — `emulsion dev`, `emulsion build`, `emulsion routes`, `emulsion new`
- **Extensions** — lifecycle hooks for plugins and integrations

## Quick Start

```bash
pip install emulsion
emulsion new my-app
cd my-app
emulsion dev
```

## Documentation

Coming soon.

## License

MIT
