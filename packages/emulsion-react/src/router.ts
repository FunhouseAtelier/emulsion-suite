/**
 * createEmulsionRouter — creates the page-level React Router instance.
 *
 * Uses createBrowserRouter (Data Mode) so that:
 * - loader functions can pre-fetch FastAPI JSON data before navigation resolves
 * - Pending states are built-in (no custom loading state management)
 * - The router instance is created programmatically from Python-derived config
 *
 * Route config is injected by the Vite plugin as window.__EMULSION_ROUTES__
 * at build time (or as a virtual module in dev).
 */

import { createBrowserRouter } from "react-router";
import type { RouteObject } from "react-router";

/** The router instance type returned by createBrowserRouter. */
export type EmulsionRouter = ReturnType<typeof createBrowserRouter>;

// ------------------------------------------------------------------
// Route config injected by @emulsion/vite-plugin
// ------------------------------------------------------------------

/** A single client-side route mirroring a Python @app.page() declaration. */
export interface EmulsionClientRoute {
  /** React Router path syntax: /products/:product_id */
  path: string;
  /** Island names present on this page — used for preload hints. */
  islands: string[];
  /** FastAPI JSON data endpoint: /products/{product_id}?format=json */
  dataUrl: string;
}

declare global {
  interface Window {
    __EMULSION_ROUTES__?: EmulsionClientRoute[];
  }
}

// ------------------------------------------------------------------
// Router factory
// ------------------------------------------------------------------

/**
 * Create the Emulsion page-level browser router.
 *
 * Called once per page load from hydration.ts.
 * The router subscribes to navigation events to trigger island re-hydration.
 */
export function createEmulsionRouter(): EmulsionRouter {
  const rawRoutes: EmulsionClientRoute[] = window.__EMULSION_ROUTES__ ?? [];

  const routeObjects: RouteObject[] = rawRoutes.map((route) => ({
    path: route.path,

    // The loader fetches page data from FastAPI before navigation completes.
    // FastAPI returns JSON when the route is called with ?format=json.
    loader: async ({ params }) => {
      const url = _buildDataUrl(route.dataUrl, params as Record<string, string>);
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Response("Not Found", { status: response.status });
      }
      return response.json() as Promise<Record<string, unknown>>;
    },

    // No React element — Emulsion's navigation handler (registered via
    // router.subscribe) performs a targeted DOM swap after loader resolves.
    element: null,
  }));

  // Catch-all: unknown routes fall through to a full FastAPI page load
  routeObjects.push({
    path: "*",
    loader: ({ request }) => {
      const { pathname, search } = new URL(request.url);
      window.location.href = pathname + search;
      return null;
    },
    element: null,
  });

  return createBrowserRouter(routeObjects);
}

// ------------------------------------------------------------------
// Helpers
// ------------------------------------------------------------------

/**
 * Replace FastAPI-style path variables in a data URL template.
 *
 * Template: /products/{product_id}?format=json
 * Params:   { product_id: "42" }
 * Result:   /products/42?format=json
 */
function _buildDataUrl(
  template: string,
  params: Record<string, string | undefined>,
): string {
  return Object.entries(params).reduce(
    (url, [key, value]) => url.replace(`{${key}}`, encodeURIComponent(value ?? "")),
    template,
  );
}
