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

/** Fill a convex quad (4 projected points) with a flat grayscale value. */
function fillQuad(png: PNG, pts: number[][], gray: number): void {
  const ys = pts.map((p) => p[1]);
  const yMin = Math.max(0, Math.floor(Math.min(...ys)));
  const yMax = Math.min(png.height - 1, Math.ceil(Math.max(...ys)));

  for (let y = yMin; y <= yMax; y++) {
    const xs: number[] = [];
    for (let e = 0; e < 4; e++) {
      const [x1, y1] = pts[e];
      const [x2, y2] = pts[(e + 1) % 4];
      if ((y1 <= y && y < y2) || (y2 <= y && y < y1)) {
        xs.push(x1 + ((y - y1) / (y2 - y1)) * (x2 - x1));
      }
    }
    if (xs.length < 2) continue;
    const xL = Math.max(0, Math.round(Math.min(...xs)));
    const xR = Math.min(png.width - 1, Math.round(Math.max(...xs)));
    for (let x = xL; x <= xR; x++) setPixel(png, x, y, gray);
  }
}

/**
 * 3D noise shown as a "Swiss cheese" cube: the field is sampled on a voxel grid,
 * the densest ~60% of voxels are kept solid (the rest become holes), and the
 * exposed faces are drawn in isometric projection (painter's order, shaded).
 */
function render3DCube(size: number): Buffer {
  const N = 24; // voxels per axis
  const STEP = 6; // noise-space distance between voxels
  const FILL = 0.6; // fraction of voxels kept solid
  const A = 4; // half tile width (px)
  const B = 2; // half tile height (px)
  const C = 4; // voxel height (px)
  const OX = size / 2;
  const OY = size / 2;
  const SHADE = { top: 215, right: 120, left: 165 };

  const perlin = new PerlinNoise3D(SEED, SCALE);
  const values = new Float64Array(N * N * N);
  const at = (i: number, j: number, k: number) => (i * N + j) * N + k;
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++)
      for (let k = 0; k < N; k++)
        values[at(i, j, k)] = perlin.noise(i * STEP, j * STEP, k * STEP);

  const threshold = [...values].sort((p, q) => p - q)[
    Math.floor(FILL * values.length)
  ];
  const solid = (i: number, j: number, k: number): boolean =>
    i >= 0 &&
    i < N &&
    j >= 0 &&
    j < N &&
    k >= 0 &&
    k < N &&
    values[at(i, j, k)] <= threshold;

  const project = (i: number, j: number, k: number): number[] => [
    OX + (i - j) * A,
    OY + (i + j) * B - k * C,
  ];

  const png = new PNG({ width: size, height: size });
  png.data.fill(255); // white background

  // Painter's algorithm: draw from the far corner to the near one.
  const voxels: number[][] = [];
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++)
      for (let k = 0; k < N; k++) if (solid(i, j, k)) voxels.push([i, j, k]);
  voxels.sort((p, q) => p[0] + p[1] + p[2] - (q[0] + q[1] + q[2]));

  for (const [i, j, k] of voxels) {
    if (!solid(i, j + 1, k)) {
      fillQuad(
        png,
        [
          project(i, j + 1, k),
          project(i + 1, j + 1, k),
          project(i + 1, j + 1, k + 1),
          project(i, j + 1, k + 1),
        ],
        SHADE.left,
      );
    }
    if (!solid(i + 1, j, k)) {
      fillQuad(
        png,
        [
          project(i + 1, j, k),
          project(i + 1, j + 1, k),
          project(i + 1, j + 1, k + 1),
          project(i + 1, j, k + 1),
        ],
        SHADE.right,
      );
    }
    if (!solid(i, j, k + 1)) {
      fillQuad(
        png,
        [
          project(i, j, k + 1),
          project(i + 1, j, k + 1),
          project(i + 1, j + 1, k + 1),
          project(i, j + 1, k + 1),
        ],
        SHADE.top,
      );
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

  it("matches the committed 3D snapshot (Swiss cheese cube)", () => {
    expectMatchesSnapshot("perlin-noise-3d.png", render3DCube(SIZE));
  });
});
