/**
 * @emulsion/react — public API
 *
 * Client-side runtime for the Emulsion framework.
 *
 * Usage (in your app's main.ts):
 *   import { hydrateIslands } from "@emulsion/react";
 *   import { registry } from "../islands/index";
 *   hydrateIslands(registry);
 */

export { hydrateIslands } from "./hydration.js";
export { Island } from "./Island.js";
export { createRegistry } from "./registry.js";
export { createEmulsionRouter } from "./router.js";

export type {
  IslandComponent,
  IslandLoader,
  IslandRegistry,
} from "./registry.js";

export type { IslandProps } from "./Island.js";
export type { EmulsionClientRoute } from "./router.js";
