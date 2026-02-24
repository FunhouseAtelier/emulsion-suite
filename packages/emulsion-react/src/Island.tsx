/**
 * <Island> — lazy wrapper component for React islands.
 *
 * Wraps each island in a React.lazy() boundary with Suspense.
 * Lazy components are cached by name to prevent unnecessary re-creates.
 *
 * Islands that declare `static needsPageRouter = true` receive the
 * page-level createBrowserRouter instance via the __pageRouter prop.
 * All other islands receive an isolated MemoryRouter (future enhancement).
 */

import React, { Suspense, useEffect, type ComponentType } from "react";
import type { IslandLoader, IslandComponent } from "./registry";
import type { RemixRouter } from "react-router";

// ------------------------------------------------------------------
// Internal cache of React.lazy() wrapped loaders, keyed by island name
// ------------------------------------------------------------------

const _lazyCache = new Map<string, React.LazyExoticComponent<IslandComponent>>();

function getLazyComponent(name: string, loader: IslandLoader) {
  if (!_lazyCache.has(name)) {
    _lazyCache.set(name, React.lazy(() => loader()));
  }
  return _lazyCache.get(name)!;
}

// ------------------------------------------------------------------
// Props
// ------------------------------------------------------------------

export interface IslandProps {
  name: string;
  props: Record<string, unknown>;
  loader: IslandLoader;
  /** The page-level router created by createBrowserRouter. */
  pageRouter: RemixRouter;
  onHydrated?: () => void;
}

// ------------------------------------------------------------------
// Inner component (rendered inside Suspense)
// ------------------------------------------------------------------

interface InnerProps {
  name: string;
  props: Record<string, unknown>;
  loader: IslandLoader;
  pageRouter: RemixRouter;
  onHydrated?: () => void;
}

function IslandInner({ name, props, loader, pageRouter, onHydrated }: InnerProps) {
  const LazyComponent = getLazyComponent(name, loader) as ComponentType<Record<string, unknown>>;

  useEffect(() => {
    onHydrated?.();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return <LazyComponent {...props} __pageRouter={pageRouter} />;
}

// ------------------------------------------------------------------
// Public <Island> component
// ------------------------------------------------------------------

/**
 * Renders an island component lazily inside a Suspense boundary.
 *
 * The fallback is `null` by default — the server-rendered placeholder
 * remains visible until the island hydrates, avoiding layout shift.
 */
export function Island({ name, props, loader, pageRouter, onHydrated }: IslandProps) {
  return (
    <Suspense fallback={null}>
      <IslandInner
        name={name}
        props={props}
        loader={loader}
        pageRouter={pageRouter}
        onHydrated={onHydrated}
      />
    </Suspense>
  );
}
