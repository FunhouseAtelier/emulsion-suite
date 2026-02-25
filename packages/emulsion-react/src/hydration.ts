/**
 * hydration.ts — client-side entry point for Emulsion island hydration.
 *
 * Responsibilities:
 * 1. Create the page-level React Router instance (createBrowserRouter)
 * 2. Scan the DOM for [data-island] placeholder divs
 * 3. Respect data-island-priority to schedule hydration appropriately
 * 4. Lazy-load each island's JS chunk and mount a React root
 * 5. Subscribe to router navigation events to re-hydrate after SPA transitions
 */

/// <reference types="vite/client" />

import { createRoot } from "react-dom/client";
import React from "react";
import { Island } from "./Island.js";
import type { IslandRegistry } from "./registry.js";
import { createEmulsionRouter } from "./router.js";
import type { EmulsionRouter } from "./router.js";

// ------------------------------------------------------------------
// Public API
// ------------------------------------------------------------------

/**
 * Initialize Emulsion island hydration.
 *
 * Call this once from your app's main.ts:
 *
 *   import { hydrateIslands } from "@emulsion/react";
 *   import { registry } from "../islands/index";
 *   hydrateIslands(registry);
 */
export function hydrateIslands(registry: IslandRegistry): void {
  const routes = window.__EMULSION_ROUTES__ ?? [];

  if (routes.length > 0) {
    // SPA mode: create router for client-side navigation between pages
    const router = createEmulsionRouter();
    _hydrateAll(registry, router);
    _subscribeToNavigations(router, registry);
  } else {
    // No routes defined (dev mode or static pages): hydrate islands only
    _hydrateAll(registry, null);
  }
}

// ------------------------------------------------------------------
// Internal: hydrate all islands on the current page
// ------------------------------------------------------------------

function _hydrateAll(registry: IslandRegistry, router: EmulsionRouter | null): void {
  const placeholders = document.querySelectorAll<HTMLElement>("[data-island]");

  placeholders.forEach((el) => {
    const name = el.getAttribute("data-island") ?? "";
    const rawProps = el.getAttribute("data-props") ?? "{}";
    const priority = el.getAttribute("data-island-priority") ?? "eager";

    if (el.getAttribute("data-hydrated") === "true") return;

    let props: Record<string, unknown>;
    try {
      props = JSON.parse(rawProps) as Record<string, unknown>;
    } catch {
      console.error(`[Emulsion] Failed to parse props for island "${name}":`, rawProps);
      return;
    }

    const loader = registry[name];
    if (!loader) {
      console.warn(`[Emulsion] No island registered for "${name}". Check your islands/index.ts.`);
      return;
    }

    const mount = () => _mountIsland(el, name, props, loader, router);
    _schedule(mount, priority, el);
  });
}

// ------------------------------------------------------------------
// Internal: mount a single island into its placeholder element
// ------------------------------------------------------------------

function _mountIsland(
  el: HTMLElement,
  name: string,
  props: Record<string, unknown>,
  loader: IslandRegistry[string],
  router: EmulsionRouter | null,
): void {
  el.setAttribute("data-hydrated", "pending");

  const root = createRoot(el);
  root.render(
    React.createElement(Island, {
      name,
      props,
      loader,
      pageRouter: router,
      onHydrated: () => {
        el.setAttribute("data-hydrated", "true");
        if (import.meta.env?.DEV) {
          console.debug(`[Emulsion] Hydrated: ${name}`);
        }
      },
    }),
  );
}

// ------------------------------------------------------------------
// Internal: priority-based scheduling
// ------------------------------------------------------------------

type HydrationPriority = "eager" | "visible" | "idle" | "interaction";

function _schedule(fn: () => void, priority: string, el: HTMLElement): void {
  switch (priority as HydrationPriority) {
    case "visible": {
      const observer = new IntersectionObserver((entries) => {
        if (entries[0]?.isIntersecting) {
          fn();
          observer.disconnect();
        }
      });
      observer.observe(el);
      break;
    }
    case "idle": {
      const ric = (window as Window & { requestIdleCallback?: (cb: () => void) => void })
        .requestIdleCallback;
      (ric ?? setTimeout)(fn);
      break;
    }
    case "interaction": {
      const once = { once: true } as const;
      el.addEventListener("mouseenter", fn, once);
      el.addEventListener("focus", fn, { ...once, capture: true });
      break;
    }
    default: // "eager"
      fn();
  }
}

// ------------------------------------------------------------------
// Internal: SPA navigation — re-hydrate after React Router transitions
// ------------------------------------------------------------------

function _subscribeToNavigations(router: EmulsionRouter, registry: IslandRegistry): void {
  let previousPathname = window.location.pathname;

  router.subscribe((state) => {
    // Only act when a navigation has fully settled
    if (state.navigation.state !== "idle") return;

    // state.location is the *current* location after navigation completes
    // (state.navigation.location only exists while navigation is in-flight)
    const currentPathname = state.location.pathname;
    if (currentPathname === previousPathname) return;
    previousPathname = currentPathname;

    // v1 strategy: fetch the new page's HTML shell from FastAPI,
    // swap <main>, then re-run hydrateAll on the new nodes.
    const targetUrl = state.location.pathname + state.location.search;

    void _swapPage(targetUrl, registry, router);
  });
}

async function _swapPage(
  url: string,
  registry: IslandRegistry,
  router: EmulsionRouter,
): Promise<void> {
  try {
    const response = await fetch(url, {
      headers: { "X-Emulsion-Partial": "1" },
    });
    if (!response.ok) return;

    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    const newMain = doc.querySelector("main");
    const currentMain = document.querySelector("main");

    if (newMain && currentMain) {
      currentMain.replaceWith(newMain);
      // Re-hydrate any new islands in the swapped content
      _hydrateAll(registry, router);
    }
  } catch (err) {
    console.error("[Emulsion] SPA navigation shell swap failed:", err);
    // Fallback: let the browser do a full navigation
    window.location.href = url;
  }
}
