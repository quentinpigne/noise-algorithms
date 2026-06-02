import { describe, it, expect } from "vitest";
import { PNG } from "pngjs";
import fs from "node:fs";
import path from "node:path";

// Import the BUILT library from dist/ — the exact artifact published to the
// registries, not the TypeScript sources.
import {
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
} from "../../dist/perlin-noise/index.mjs";

const SEED = 42;
const SCALE = 0.03;
const SIZE = 256;
const STRIP_HEIGHT = 64;

const SNAPSHOT_DIR = path.resolve(__dirname, "../snapshots");
const OUTPUT_DIR = path.resolve(__dirname, "../output");

/** Map a noise value in [-1, 1] to a grayscale byte in [0, 255]. */
function toGray(value: number): number {
  return Math.max(0, Math.min(255, Math.floor(((value + 1) / 2) * 255)));
}

/** Build an RGBA PNG buffer from a per-pixel grayscale function. */
function renderPNG(
  width: number,
  height: number,
  grayAt: (x: number, y: number) => number,
): Buffer {
  const png = new PNG({ width, height });
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (width * y + x) << 2;
      const gray = grayAt(x, y);
      png.data[idx] = gray;
      png.data[idx + 1] = gray;
      png.data[idx + 2] = gray;
      png.data[idx + 3] = 255;
    }
  }
  return PNG.sync.write(png);
}

/** Render the noise to PNG, persist the output, and assert it matches snapshot. */
function expectMatchesSnapshot(name: string, generated: Buffer): void {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUTPUT_DIR, name), generated);

  const snapshot = path.join(SNAPSHOT_DIR, name);
  if (process.env.UPDATE_SNAPSHOTS || !fs.existsSync(snapshot)) {
    fs.mkdirSync(SNAPSHOT_DIR, { recursive: true });
    fs.writeFileSync(snapshot, generated);
  }

  // Compare decoded pixels (robust to PNG encoder differences).
  const generatedPixels = PNG.sync.read(generated).data;
  const snapshotPixels = PNG.sync.read(fs.readFileSync(snapshot)).data;
  expect(Buffer.compare(generatedPixels, snapshotPixels)).toBe(0);
}

describe("Perlin noise image (built library)", () => {
  it("matches the committed 1D snapshot", () => {
    const perlin = new PerlinNoise1D(SEED, SCALE);
    const generated = renderPNG(SIZE, STRIP_HEIGHT, (x) =>
      toGray(perlin.noise(x)),
    );
    expectMatchesSnapshot("perlin-noise-1d.png", generated);
  });

  it("matches the committed 2D snapshot", () => {
    const perlin = new PerlinNoise2D(SEED, SCALE);
    const generated = renderPNG(SIZE, SIZE, (x, y) =>
      toGray(perlin.noise(x, y)),
    );
    expectMatchesSnapshot("perlin-noise-2d.png", generated);
  });

  it("matches the committed 3D snapshot (z = 0 slice)", () => {
    const perlin = new PerlinNoise3D(SEED, SCALE);
    const generated = renderPNG(SIZE, SIZE, (x, y) =>
      toGray(perlin.noise(x, y, 0)),
    );
    expectMatchesSnapshot("perlin-noise-3d.png", generated);
  });
});
