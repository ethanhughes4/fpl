/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite serves the page on this PC only (localhost, D298); Vitest runs the tests in jsdom, a fake browser.
export default defineConfig({
  plugins: [react()],
  server: { host: "localhost", port: 5173 },
  test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"] },
});
