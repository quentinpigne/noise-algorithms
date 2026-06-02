import { describe, it, expect } from "vitest";
import { PNG } from "pngjs";
import fs from "node:fs";
import path from "node:path";

// Import the BUILT library from dist/ — the exact artifact published to the
// registries, not the TypeScript sources.
import { PerlinNoise2D } from "../../dist/perlin-noise/index.mjs";

const WIDTH = 256;
const HEIGHT = 256;
const SEED = 42;
const SCALE = 0.03;

const SNAPSHOT = path.resolve(__dirname, "../snapshots/perlin-noise-2d.png");
const OUTPUT_DIR = path.resolve(__dirname, "../output");
const OUTPUT = path.join(OUTPUT_DIR, "perlin-noise-2d.png");

/** Render a deterministic 2D Perlin noise field into an RGBA PNG buffer. */
function renderNoise(): Buffer {
  const perlin = new PerlinNoise2D(SEED, SCALE);
  const png = new PNG({ width: WIDTH, height: HEIGHT });

  for (let y = 0; y < HEIGHT; y++) {
    for (let x = 0; x < WIDTH; x++) {
      const value = perlin.noise(x, y);
      const gray = Math.max(
        0,
        Math.min(255, Math.floor(((value + 1) / 2) * 255)),
      );
      const idx = (WIDTH * y + x) << 2;
      png.data[idx] = gray;
      png.data[idx + 1] = gray;
      png.data[idx + 2] = gray;
      png.data[idx + 3] = 255;
    }
  }

  return PNG.sync.write(png);
}

describe("Perlin noise image (built library)", () => {
  it("matches the committed 2D snapshot", () => {
    const generated = renderNoise();

    // Always write the generated image so it can be inspected / diffed.
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    fs.writeFileSync(OUTPUT, generated);

    // Refresh the snapshot on demand or on first run.
    if (process.env.UPDATE_SNAPSHOTS || !fs.existsSync(SNAPSHOT)) {
      fs.mkdirSync(path.dirname(SNAPSHOT), { recursive: true });
      fs.writeFileSync(SNAPSHOT, generated);
    }

    // Compare decoded pixels (robust to PNG encoder differences).
    const generatedPixels = PNG.sync.read(generated).data;
    const snapshotPixels = PNG.sync.read(fs.readFileSync(SNAPSHOT)).data;

    expect(Buffer.compare(generatedPixels, snapshotPixels)).toBe(0);
  });
});
