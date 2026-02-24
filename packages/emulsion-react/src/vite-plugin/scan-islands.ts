/**
 * scan-islands.ts — discover island components in the user's islands/ directory.
 *
 * Convention:  Any .tsx or .jsx file exported as default from <islandsDir>/ is
 *              treated as an island.  The island name is the filename stem.
 *
 * Returns a Map<name, absoluteFilePath>.
 */

import { readdirSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";

const ISLAND_EXTENSIONS = new Set([".tsx", ".jsx"]);

/**
 * Scan a directory for island component files.
 *
 * @param islandsDir - Absolute or relative path to the islands directory.
 * @returns Map of island name → absolute file path.
 */
export function scanIslands(islandsDir: string): Map<string, string> {
  const absDir = resolve(islandsDir);
  const result = new Map<string, string>();

  let entries: string[];
  try {
    entries = readdirSync(absDir);
  } catch {
    // Directory doesn't exist yet — return empty map gracefully
    return result;
  }

  for (const entry of entries) {
    const fullPath = join(absDir, entry);
    const ext = extname(entry);

    if (!ISLAND_EXTENSIONS.has(ext)) continue;

    const stat = statSync(fullPath);
    if (!stat.isFile()) continue;

    // Skip barrel files (index.tsx, index.jsx) — they are auto-generated
    const stem = entry.slice(0, -ext.length);
    if (stem.toLowerCase() === "index") continue;

    result.set(stem, fullPath);
  }

  return result;
}
