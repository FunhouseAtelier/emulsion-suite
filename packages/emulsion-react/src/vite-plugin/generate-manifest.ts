/**
 * generate-manifest.ts — produce island-manifest.json after Vite build.
 *
 * The manifest maps island names to their hashed output filenames.
 * The Python IslandManifest class reads this at application startup.
 *
 * Manifest format:
 * {
 *   "version": 1,
 *   "generated": "<ISO timestamp>",
 *   "hydrationEntry": { "file": "islands/emulsion-hydration-Abc.js", "css": [] },
 *   "islands": {
 *     "Counter": { "file": "islands/Counter-Def.js", "css": [], "imports": [] }
 *   },
 *   "sharedChunks": {}
 * }
 */

import type { OutputBundle, OutputChunk } from "rollup";

export interface IslandManifestEntry {
  file: string;
  css: string[];
  imports: string[];
}

export interface IslandManifestData {
  version: number;
  generated: string;
  hydrationEntry: IslandManifestEntry;
  islands: Record<string, IslandManifestEntry>;
  sharedChunks: Record<string, string>;
}

const HYDRATION_ENTRY_NAME = "emulsion-hydration";

/**
 * Build the island manifest from a completed Rollup output bundle.
 *
 * @param bundle        - The Rollup OutputBundle from generateBundle hook.
 * @param islandNames   - Map of island name → source file path (from scan-islands).
 * @returns             The manifest data object (caller writes it to disk).
 */
export function generateManifest(
  bundle: OutputBundle,
  islandNames: Map<string, string>,
): IslandManifestData {
  // Index all output chunks by their facadeModuleId (source file path)
  const chunkBySource = new Map<string, OutputChunk>();
  const chunkByName = new Map<string, OutputChunk>();

  for (const file of Object.values(bundle)) {
    if (file.type !== "chunk") continue;
    if (file.facadeModuleId) {
      chunkBySource.set(file.facadeModuleId, file);
    }
    chunkByName.set(file.name, file);
  }

  // Locate the hydration entry chunk
  const hydrationChunk =
    chunkByName.get(HYDRATION_ENTRY_NAME) ??
    _findChunkByNamePattern(bundle, HYDRATION_ENTRY_NAME);

  const hydrationEntry: IslandManifestEntry = hydrationChunk
    ? _chunkToEntry(hydrationChunk, bundle)
    : { file: "", css: [], imports: [] };

  // Build the islands map
  const islands: Record<string, IslandManifestEntry> = {};

  for (const [name, sourcePath] of islandNames) {
    const chunk = chunkBySource.get(sourcePath);
    if (!chunk) {
      console.warn(`[emulsion] No output chunk found for island "${name}" (${sourcePath})`);
      continue;
    }
    islands[name] = _chunkToEntry(chunk, bundle);
  }

  // Identify shared chunks (not an island or hydration entry)
  const islandFileSet = new Set([
    hydrationEntry.file,
    ...Object.values(islands).map((e) => e.file),
  ]);
  const sharedChunks: Record<string, string> = {};

  for (const file of Object.values(bundle)) {
    if (file.type !== "chunk") continue;
    if (!islandFileSet.has(file.fileName) && !file.isEntry) {
      sharedChunks[file.name] = file.fileName;
    }
  }

  return {
    version: 1,
    generated: new Date().toISOString(),
    hydrationEntry,
    islands,
    sharedChunks,
  };
}

// ------------------------------------------------------------------
// Helpers
// ------------------------------------------------------------------

function _chunkToEntry(chunk: OutputChunk, bundle: OutputBundle): IslandManifestEntry {
  // Collect CSS files that belong to this chunk via vite's asset references
  const css: string[] = [];
  for (const assetFile of Object.values(bundle)) {
    if (
      assetFile.type === "asset" &&
      typeof assetFile.fileName === "string" &&
      assetFile.fileName.endsWith(".css") &&
      (chunk.viteMetadata?.importedCss?.has(assetFile.fileName) ?? false)
    ) {
      css.push(assetFile.fileName);
    }
  }

  return {
    file: chunk.fileName,
    css,
    imports: chunk.imports.filter((f) => !f.startsWith("http")),
  };
}

function _findChunkByNamePattern(bundle: OutputBundle, pattern: string): OutputChunk | undefined {
  for (const file of Object.values(bundle)) {
    if (file.type === "chunk" && file.fileName.includes(pattern)) {
      return file;
    }
  }
  return undefined;
}
