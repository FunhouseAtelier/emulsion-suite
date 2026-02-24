import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { emulsion } from "@emulsion/react/vite-plugin";

export default defineConfig({
  plugins: [
    react(),
    emulsion({
      islandsDir: "./islands",
      hydrationEntry: "./src/main.ts",
      manifestOutput: "static/.vite/island-manifest.json",
    }),
  ],
  build: {
    manifest: true,
    rollupOptions: {
      output: {
        dir: "static",
        entryFileNames: "islands/[name]-[hash].js",
        chunkFileNames: "islands/chunks/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
  server: {
    port: 5173,
    cors: true,
    // Allow FastAPI templates (port 8000) to load scripts from the Vite dev server
    origin: "http://localhost:5173",
  },
});
