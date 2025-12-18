import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts", "src/perlin-noise/index.ts"],
  format: ["esm"],
  clean: true,
  dts: true,
});
