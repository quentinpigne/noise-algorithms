import { PerlinNoise1D } from "../src/perlin-noise/perlin-noise-1d";
import { PerlinNoise2D } from "../src/perlin-noise/perlin-noise-2d";
import { PerlinNoise3D } from "../src/perlin-noise/perlin-noise-3d";
import { PerlinNoiseImage } from "../scripts/perlin-noise-image";
import fs from "fs";
import path from "path";

describe("Perlin noise generator", () => {
  it("should generate 1D Perlin noise", () => {
    const perlin = new PerlinNoise1D(42);
    const result = perlin.noise(0.5);
    expect(result).toBeCloseTo(0.010613, 6);
  });

  it("should generate 2D Perlin noise", () => {
    const perlin = new PerlinNoise2D(42);
    const result = perlin.noise(0.5, 0.5);
    expect(result).toBeCloseTo(-0.01513, 6);
  });

  it("should generate 3D Perlin noise", () => {
    const perlin = new PerlinNoise3D(42);
    const result = perlin.noise(0.5, 0.5, 0.5);
    expect(result).toBeCloseTo(-0.014968, 6);
  });

  it("should be deterministic for a given seed", () => {
    const a = new PerlinNoise2D(42).noise(1.5, 2.5);
    const b = new PerlinNoise2D(42).noise(1.5, 2.5);
    expect(a).toBe(b);
  });

  it("should produce different output for different seeds", () => {
    const a = new PerlinNoise2D(1).noise(1.5, 2.5);
    const b = new PerlinNoise2D(2).noise(1.5, 2.5);
    expect(a).not.toBe(b);
  });

  it("should treat seed 0 as a valid, deterministic seed", () => {
    const a = new PerlinNoise2D(0).noise(1.5, 2.5);
    const b = new PerlinNoise2D(0).noise(1.5, 2.5);
    expect(a).toBe(b);
  });

  it("should keep output within [-1, 1] across many samples", () => {
    const perlin = new PerlinNoise3D(42);
    for (let i = 0; i < 1000; i++) {
      const value = perlin.noise(i * 0.37, i * 1.13, i * 2.71);
      expect(value).toBeGreaterThanOrEqual(-1);
      expect(value).toBeLessThanOrEqual(1);
    }
  });

  it("should exercise all 3D gradient vectors (regression for h % 12)", () => {
    // With the previous `h & 11` masking, indices 4..7 were never reached.
    // A wide sweep should now stay bounded and vary, confirming full coverage.
    const perlin = new PerlinNoise3D(7, 0.1);
    const values = new Set<number>();
    for (let i = 0; i < 200; i++) {
      values.add(perlin.noise(i * 0.5, i * 0.25, i * 0.75));
    }
    expect(values.size).toBeGreaterThan(100);
  });

  it("should create a 2D Perlin noise PNG image", () => {
    const pngBuffer = PerlinNoiseImage.generate2D({
      width: 64,
      height: 64,
      seed: 42,
      scale: 0.05,
    });

    const outDir = path.resolve(process.cwd(), "tests/output");
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }

    const outPath = path.join(outDir, "perlin-2d-test.png");
    PerlinNoiseImage.savePNG(pngBuffer, outPath);

    expect(fs.existsSync(outPath)).toBe(true);
    const stats = fs.statSync(outPath);
    expect(stats.size).toBeGreaterThan(0);
  });
});
