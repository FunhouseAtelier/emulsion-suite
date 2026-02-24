/**
 * Emulsion island hydration entry point.
 *
 * This file is the Vite entry (emulsion-hydration) loaded on every page.
 * It imports the island registry and starts hydration.
 */

import { hydrateIslands } from "@emulsion/react";
import { registry } from "../islands/index";

hydrateIslands(registry);
