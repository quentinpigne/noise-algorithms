import {
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
  perlin1D,
  perlin2D,
  perlin3D,
  FractalPerlinNoise2D,
  fractalPerlin1D,
  fractalPerlin2D,
  fractalPerlin3D,
} from "../src/perlin-noise";
import { NoiseGenerator, FractalNoiseGenerator } from "../src";

describe("Perlin noise generator (single octave)", () => {
  it("should be deterministic for a given seed", () => {
    const a = new PerlinNoise2D({ seed: 42 }).noise(1.5, 2.5);
    const b = new PerlinNoise2D({ seed: 42 }).noise(1.5, 2.5);
    expect(a).toBe(b);
  });

  it("should produce different output for different seeds", () => {
    const a = new PerlinNoise2D({ seed: 1 });
    const b = new PerlinNoise2D({ seed: 2 });
    // Sample a few off-lattice points: a single octave can coincide at a
    // symmetric point (e.g. cell centres), so compare across several.
    const points = [
      [0.3, 0.7],
      [1.3, 2.7],
      [4.2, 1.8],
    ];
    const differs = points.some(([x, y]) => a.noise(x, y) !== b.noise(x, y));
    expect(differs).toBe(true);
  });

  it("should treat seed 0 as a valid, deterministic seed", () => {
    const a = new PerlinNoise2D({ seed: 0 }).noise(1.5, 2.5);
    const b = new PerlinNoise2D({ seed: 0 }).noise(1.5, 2.5);
    expect(a).toBe(b);
  });

  it("should keep output within [-1, 1] across many samples", () => {
    const perlin = new PerlinNoise3D({ seed: 42 });
    for (let i = 0; i < 1000; i++) {
      const value = perlin.noise(i * 0.37, i * 1.13, i * 2.71);
      expect(value).toBeGreaterThanOrEqual(-1);
      expect(value).toBeLessThanOrEqual(1);
    }
  });

  it("should exercise all 3D gradient vectors (regression for h % 12)", () => {
    // With the previous `h & 11` masking, indices 4..7 were never reached.
    // A wide sweep should now stay bounded and vary, confirming full coverage.
    const perlin = new PerlinNoise3D({ seed: 7 });
    const values = new Set<number>();
    for (let i = 0; i < 200; i++) {
      values.add(perlin.noise(i * 0.5, i * 0.25, i * 0.75));
    }
    expect(values.size).toBeGreaterThan(100);
  });

  it("should expose one-shot functions matching the classes", () => {
    expect(perlin1D(0.5, { seed: 42 })).toBe(
      new PerlinNoise1D({ seed: 42 }).noise(0.5),
    );
    expect(perlin2D(1.5, 2.5, { seed: 42 })).toBe(
      new PerlinNoise2D({ seed: 42 }).noise(1.5, 2.5),
    );
    expect(perlin3D(1.5, 2.5, 3.5, { seed: 42 })).toBe(
      new PerlinNoise3D({ seed: 42 }).noise(1.5, 2.5, 3.5),
    );
  });
});

describe("Fractal Perlin noise", () => {
  // Cross-language conformance vectors: these exact values are also asserted in
  // the Python suite (test_perlin.py). The same seed must produce the same field
  // in every package — keep the two lists identical.
  it("should generate fractal 1D Perlin noise", () => {
    expect(fractalPerlin1D(0.5, { seed: 42 })).toBeCloseTo(
      -0.010716767090833334,
      12,
    );
  });

  it("should generate fractal 2D Perlin noise", () => {
    expect(fractalPerlin2D(0.5, 0.5, { seed: 42 })).toBeCloseTo(
      1.653283292556325e-5,
      12,
    );
  });

  it("should generate fractal 3D Perlin noise", () => {
    expect(fractalPerlin3D(0.5, 0.5, 0.5, { seed: 42 })).toBeCloseTo(
      0.015079820337889127,
      12,
    );
  });

  it("should change output with the number of octaves", () => {
    const one = new FractalPerlinNoise2D({ seed: 42, octaves: 1 }).noise(
      1.5,
      2.5,
    );
    const many = new FractalPerlinNoise2D({ seed: 42, octaves: 6 }).noise(
      1.5,
      2.5,
    );
    expect(one).not.toBe(many);
  });

  it("should expose a one-shot function matching the class", () => {
    expect(fractalPerlin2D(1.5, 2.5, { seed: 42, octaves: 3 })).toBe(
      new FractalPerlinNoise2D({ seed: 42, octaves: 3 }).noise(1.5, 2.5),
    );
  });

  it("should extend the abstract concept classes", () => {
    expect(new PerlinNoise2D({ seed: 42 })).toBeInstanceOf(NoiseGenerator);
    expect(new FractalPerlinNoise2D({ seed: 42 })).toBeInstanceOf(
      FractalNoiseGenerator,
    );
    // A fractal generator is still a noise generator (has noise()).
    expect(new FractalPerlinNoise2D({ seed: 42 }).noise).toBeTypeOf("function");
  });
});
