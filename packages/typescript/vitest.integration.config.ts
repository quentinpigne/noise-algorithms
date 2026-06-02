import { defineConfig } from "vitest/config";

// Integration tests run against the built library in dist/ (run `npm run build`
// first, or use `npm run test:integration`).
export default defineConfig({
  test: {
    environment: "node",
    globals: true,
    include: ["tests/integration/**/*.spec.ts"],
  },
});
