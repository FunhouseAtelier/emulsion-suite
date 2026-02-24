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

export { hydrateIslands } from "./hydration";
export { Island } from "./Island";
export { createRegistry } from "./registry";
export { createEmulsionRouter } from "./router";

export type {
  IslandComponent,
  IslandLoader,
  IslandRegistry,
} from "./registry";

export type { IslandProps } from "./Island";
export type { EmulsionClientRoute } from "./router";
