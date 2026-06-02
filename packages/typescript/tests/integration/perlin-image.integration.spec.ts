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

const SNAPSHOT_DIR = path.resolve(__dirname, "../snapshots");
const OUTPUT_DIR = path.resolve(__dirname, "../output");

/** Map a noise value in [-1, 1] to a grayscale byte in [0, 255]. */
function toGray(value: number): number {
  return Math.max(0, Math.min(255, Math.floor(((value + 1) / 2) * 255)));
}

function setPixel(png: PNG, x: number, y: number, gray: number): void {
  const idx = (png.width * y + x) << 2;
  png.data[idx] = gray;
  png.data[idx + 1] = gray;
  png.data[idx + 2] = gray;
  png.data[idx + 3] = 255;
}

/** 1D noise drawn as a line graph: x = position, y = noise value. */
function render1DGraph(width: number, height: number): Buffer {
  const perlin = new PerlinNoise1D(SEED, SCALE);
  const png = new PNG({ width, height });
  png.data.fill(255); // white background

  const midline = Math.floor(height / 2);
  for (let x = 0; x < width; x++) setPixel(png, x, midline, 210); // zero axis

  let previous: number | null = null;
  for (let x = 0; x < width; x++) {
    const value = perlin.noise(x);
    const y = Math.max(
      0,
      Math.min(height - 1, Math.round((1 - (value + 1) / 2) * (height - 1))),
    );
    const lo = previous === null ? y : Math.min(previous, y);
    const hi = previous === null ? y : Math.max(previous, y);
    for (let yy = lo; yy <= hi; yy++) setPixel(png, x, yy, 30); // dark curve
    previous = y;
  }

  return PNG.sync.write(png);
}

/** 2D noise rendered as a grayscale field. */
function render2DField(size: number): Buffer {
  const perlin = new PerlinNoise2D(SEED, SCALE);
  const png = new PNG({ width: size, height: size });
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      setPixel(png, x, y, toGray(perlin.noise(x, y)));
    }
  }
  return PNG.sync.write(png);
}

/**
 * 3D noise shown as a montage of z-slices: a grid of tiles, each sampling the
 * full field at an increasing depth z, so the third dimension is visible.
 */
function render3DMontage(size: number): Buffer {
  const GRID = 4;
  const TILE = size / GRID;
  const STRIDE = size / TILE;
  const Z_STEP = 8;

  const perlin = new PerlinNoise3D(SEED, SCALE);
  const png = new PNG({ width: size, height: size });

  for (let k = 0; k < GRID * GRID; k++) {
    const col = k % GRID;
    const row = Math.floor(k / GRID);
    const z = k * Z_STEP;
    for (let ty = 0; ty < TILE; ty++) {
      for (let tx = 0; tx < TILE; tx++) {
        const value = perlin.noise(tx * STRIDE, ty * STRIDE, z);
        setPixel(png, col * TILE + tx, row * TILE + ty, toGray(value));
      }
    }
  }

  // White separators between tiles.
  for (let i = 1; i < GRID; i++) {
    for (let p = 0; p < size; p++) {
      setPixel(png, i * TILE, p, 255);
      setPixel(png, p, i * TILE, 255);
    }
  }

  return PNG.sync.write(png);
}

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
    expectMatchesSnapshot("perlin-noise-1d.png", render1DGraph(512, 256));
  });

  it("matches the committed 2D snapshot", () => {
    expectMatchesSnapshot("perlin-noise-2d.png", render2DField(SIZE));
  });

  it("matches the committed 3D snapshot (z-slice montage)", () => {
    expectMatchesSnapshot("perlin-noise-3d.png", render3DMontage(SIZE));
  });
});
