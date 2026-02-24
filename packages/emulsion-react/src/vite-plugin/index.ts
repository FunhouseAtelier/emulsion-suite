/**
 * @emulsion/react/vite-plugin — Vite plugin for Emulsion island builds.
 *
 * Responsibilities:
 * 1. buildStart:       Scan islands/ directory, inject multi-entry Rollup inputs
 * 2. generateBundle:   Emit island-manifest.json after build
 * 3. resolveId/load:   Serve virtual:emulsion-registry in dev mode
 * 4. handleHotUpdate:  Full reload when island source files change
 *
 * Usage (vite.config.ts):
 *   import { emulsion } from "@emulsion/react/vite-plugin";
 *   export default defineConfig({
 *     plugins: [react(), emulsion({ islandsDir: "./islands", hydrationEntry: "./src/main.ts" })],
 *   });
 */

import { readFileSync } from "node:fs";
import { resolve, join, dirname } from "node:path";
import type { Plugin, ResolvedConfig } from "vite";
import type { NormalizedOutputOptions, OutputBundle } from "rollup";
import { scanIslands } from "./scan-islands";
import { generateManifest } from "./generate-manifest";

// ------------------------------------------------------------------
// Plugin options
// ------------------------------------------------------------------

export interface EmulsionPluginOptions {
  /** Directory containing island .tsx/.jsx components. Default: "./islands" */
  islandsDir?: string;
  /** Hydration entry point loaded on every page. Default: "./src/main.ts" */
  hydrationEntry?: string;
  /**
   * Where to write the island manifest JSON (relative to project root).
   * Default: "static/.vite/island-manifest.json"
   */
  manifestOutput?: string;
}

const VIRTUAL_REGISTRY_ID = "virtual:emulsion-registry";
const RESOLVED_VIRTUAL_REGISTRY_ID = "\0" + VIRTUAL_REGISTRY_ID;

// ------------------------------------------------------------------
// Plugin factory
// ------------------------------------------------------------------

export function emulsion(options: EmulsionPluginOptions = {}): Plugin {
  const islandsDir = options.islandsDir ?? "./islands";
  const hydrationEntry = options.hydrationEntry ?? "./src/main.ts";
  const manifestOutput = options.manifestOutput ?? "static/.vite/island-manifest.json";

  let resolvedConfig: ResolvedConfig;
  let discoveredIslands: Map<string, string> = new Map();

  return {
    name: "@emulsion/vite-plugin",
    enforce: "pre",

    configResolved(config) {
      resolvedConfig = config;
    },

    // ------------------------------------------------------------------
    // Build start: discover islands and inject Rollup entry points
    // ------------------------------------------------------------------

    async buildStart() {
      const absIslandsDir = resolve(resolvedConfig.root, islandsDir);
      const absHydrationEntry = resolve(resolvedConfig.root, hydrationEntry);

      discoveredIslands = scanIslands(absIslandsDir);

      // Build the multi-entry input record for Rollup
      const inputs: Record<string, string> = {
        "emulsion-hydration": absHydrationEntry,
      };

      for (const [name, filePath] of discoveredIslands) {
        inputs[`islands/${name}`] = filePath;
      }

      // Patch rollupOptions.input (must use Object.assign to mutate the
      // resolved config's reference; Vite re-reads this before bundling)
      const existing = resolvedConfig.build.rollupOptions.input;
      if (typeof existing === "string" || Array.isArray(existing)) {
        // Wrap existing string/array entry
        const wrapped: Record<string, string> =
          typeof existing === "string"
            ? { index: existing }
            : Object.fromEntries(existing.map((e, i) => [`entry-${i}`, e]));
        Object.assign(wrapped, inputs);
        resolvedConfig.build.rollupOptions.input = wrapped;
      } else {
        Object.assign(existing ?? {}, inputs);
        resolvedConfig.build.rollupOptions.input = { ...(existing ?? {}), ...inputs };
      }

      if (resolvedConfig.command === "build") {
        console.log(
          `[emulsion] Found ${discoveredIslands.size} island(s): ${[...discoveredIslands.keys()].join(", ")}`,
        );
      }
    },

    // ------------------------------------------------------------------
    // After build: write the island manifest
    // ------------------------------------------------------------------

    generateBundle(_options: NormalizedOutputOptions, bundle: OutputBundle) {
      const manifest = generateManifest(bundle, discoveredIslands);
      const json = JSON.stringify(manifest, null, 2);

      this.emitFile({
        type: "asset",
        fileName: ".vite/island-manifest.json",
        source: json,
      });
    },

    // ------------------------------------------------------------------
    // Dev mode: serve virtual:emulsion-registry module
    // ------------------------------------------------------------------

    resolveId(id: string) {
      if (id === VIRTUAL_REGISTRY_ID) return RESOLVED_VIRTUAL_REGISTRY_ID;
    },

    async load(id: string) {
      if (id !== RESOLVED_VIRTUAL_REGISTRY_ID) return;

      // Re-scan islands on each load so new files appear immediately in dev
      const absIslandsDir = resolve(resolvedConfig.root, islandsDir);
      const islands = scanIslands(absIslandsDir);

      const lines = [...islands.entries()].map(
        ([name, path]) =>
          `  ${JSON.stringify(name)}: () => import(${JSON.stringify(path)}),`,
      );

      return (
        `import { createRegistry } from "@emulsion/react";\n` +
        `export const registry = createRegistry({\n${lines.join("\n")}\n});\n`
      );
    },

    // ------------------------------------------------------------------
    // HMR: full reload when island source files change
    // ------------------------------------------------------------------

    handleHotUpdate({ file, server }) {
      const absIslandsDir = resolve(resolvedConfig.root, islandsDir);
      if (file.startsWith(absIslandsDir)) {
        console.log(`[emulsion] Island changed: ${file} — reloading`);
        server.ws.send({ type: "full-reload" });
        // Returning [] prevents Vite from doing its own HMR (which would fail
        // since the virtual registry needs to be regenerated)
        return [];
      }
    },
  };
}

// Re-export for convenience
export type { EmulsionPluginOptions as EmulsionOptions };
