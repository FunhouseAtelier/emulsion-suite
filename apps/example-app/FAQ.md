# Example App — FAQ

Answers to common questions about the files at the root of this app.

---

## `main.py`

### Where does `from emulsion import EmulsionApp, EmulsionPage` come from?

In the monorepo it resolves to `packages/emulsion/src/emulsion/__init__.py`, because the package is installed in editable mode (`uv pip install -e packages/emulsion`). Changes to that source tree take effect immediately with no reinstall.

In a regular project it would be installed from PyPI (`pip install emulsion`) and the import is identical — the package name is `emulsion` in both cases.

### What does the `title` argument to `EmulsionApp` do?

It is passed to FastAPI as the application title, which appears in the auto-generated OpenAPI schema (`/openapi.json`) and the interactive docs at `/docs`. It does not appear in Jinja2 templates unless you reference it explicitly.

### What does `debug=True` do?

It is passed to two places:

1. **FastAPI** — enables full exception tracebacks in HTTP error responses instead of generic 500 pages.
2. **Jinja2** — sets `auto_reload=True`, so templates are re-read from disk on every render rather than cached. This lets you edit templates without restarting the server.

`debug=True` should not be hardcoded in production as it leaks internal stack traces. Drive it from an environment variable instead.

### Why are page handlers classes rather than functions?

Several reasons:

- **Structured metadata** — `template`, `islands`, and `title` live as class attributes alongside the handler logic, keeping the full page definition self-contained.
- **Dual-response dispatch** — every page must respond to both HTML requests and `?format=json` (for React Router SPA navigation). The base class handles that dispatch via `_render_html()` / `_render_json()`; you only write `data()`.
- **`self.request`** — the request is stored on the instance, so any helper method you add to the class has access to it without threading it through every function signature.
- **Extensibility** — you can subclass `EmulsionPage` to create shared base classes (e.g. `AuthenticatedPage`) that override `_render_html()` without touching page-specific code.

---

## `package.json`

### What is the difference between `dev` and `preview`?

`dev` runs FastAPI and Vite concurrently and sets `EMULSION_DEV_MODE=true`. Vite provides HMR and the React refresh preamble is injected into every page. Use this for active development.

`preview` runs uvicorn only, with no Vite and no dev mode flag. Its purpose is to serve a production build locally before deploying:

```bash
emulsion build   # compile islands → static/
pnpm preview     # serve the result with plain uvicorn
```

`vite_scripts()` falls through to the manifest path, reads `static/.vite/island-manifest.json`, and emits hashed `<script>` tags — exactly what a production server would serve.

### What does `"@emulsion/react": "workspace:*"` mean?

`workspace:` tells pnpm to use the local monorepo copy of `@emulsion/react` rather than fetching from npm. The `*` is the version constraint — it means "any version," which is idiomatic during active development. pnpm resolves the name by scanning workspace packages (defined in `pnpm-workspace.yaml`) for the one whose `package.json` declares `"name": "@emulsion/react"`, then symlinks `node_modules/@emulsion/react` → `packages/emulsion-react/`.

When changesets publishes a release it rewrites `workspace:*` to the actual resolved version (e.g. `"0.1.0"`) in the published manifest automatically.

---

## `tsconfig.json`

Standard TypeScript config for a modern Vite/React project. Notable settings:

- **`moduleResolution: bundler`** — tells TypeScript that Vite handles resolution, so relative imports in app source don't need `.js` extensions (unlike the `@emulsion/react` package itself, whose compiled output is consumed directly by Node.js and does require them).
- **`jsx: react-jsx`** — uses React 17+'s automatic JSX transform; island files don't need `import React from "react"`.
- **`include`** covers `src/`, `islands/`, and `vite.config.ts` so VS Code type-checks all of them in the same project context.
- **`exclude: ["static"]`** keeps the built output out of the TypeScript project.

---

## `vite.config.ts`

The `@emulsion/react/vite-plugin` handles island discovery, registry generation, and manifest output. The `build.rollupOptions` block configures output paths for hashed island bundles, chunks, and assets under `static/`.

The `server` block deserves attention:

```ts
server: {
  cors: true,
  origin: "http://localhost:5173",
}
```

- **`origin`** — tells Vite to prefix all injected asset URLs with `http://localhost:5173`. Without it, Vite can produce relative URLs that break when HTML is served from `:8000` instead of `:5173`.
- **`cors: true`** — sends `Access-Control-Allow-Origin` headers so the browser allows cross-origin requests from `:8000` to `:5173`.

Together these two settings are what make the FastAPI + Vite split-server dev model work.
