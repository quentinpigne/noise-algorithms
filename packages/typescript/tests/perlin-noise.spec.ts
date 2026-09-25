import {
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
  perlin1D,
  perlin2D,
  perlin3D,
  FractalPerlinNoise2D,
  FractalPerlinNoise3D,
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

  it("should exercise the 3D gradient set across a wide sweep", () => {
    // The `h & 15` selection reaches every gradient; a wide sweep should stay
    // bounded and produce many distinct values, confirming broad coverage.
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
  //
  // They are asserted with `toBe`, not `toBeCloseTo`. The invariant these vectors
  // guard is bit-for-bit identity, and a tolerance cannot express it: at twelve
  // decimals a value may drift by thousands of ULPs and still pass, so the
  // assertion would agree while the field quietly differed. Each literal is the
  // shortest decimal that round-trips to its f64, and parses to the same bits in
  // JavaScript and in Python — verified against the raw bytes.
  it("should generate fractal 1D Perlin noise", () => {
    // bf95f2ac21644eb3
    expect(fractalPerlin1D(0.5, { seed: 42 })).toBe(-0.02143353418166667);
  });

  it("should generate fractal 2D Perlin noise", () => {
    // 3ef88447197c25d4
    expect(fractalPerlin2D(0.5, 0.5, { seed: 42 })).toBe(2.338095654778e-5);
  });

  it("should generate fractal 3D Perlin noise", () => {
    // 3f95d67e147f7673
    expect(fractalPerlin3D(0.5, 0.5, 0.5, { seed: 42 })).toBe(
      0.021326036454289054,
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

describe("Weighted and independent octaves", () => {
  const INDEPENDENT = {
    seed: 42,
    amplitudes: [1, 2, 0, 1],
    independentOctaves: true,
    frequency: 0.25,
  };

  // Cross-language conformance vectors, also asserted in test_perlin.py: the
  // octave sources are drawn from the seed in a fixed order, and both packages
  // must draw the same ones.
  it("should generate independent 1D octaves", () => {
    // 3faf260910126dc4
    expect(fractalPerlin1D(0.5, INDEPENDENT)).toBe(0.060837062084114574);
  });

  it("should generate independent 2D octaves", () => {
    // 3fd58e9aacade759
    expect(fractalPerlin2D(0.5, 0.5, INDEPENDENT)).toBe(0.33682886946882246);
  });

  it("should generate independent 3D octaves", () => {
    // bf930db1f85f822d
    expect(fractalPerlin3D(0.5, 0.5, 0.5, INDEPENDENT)).toBe(
      -0.01860693052720046,
    );
  });

  it("should weight shared octaves", () => {
    // 3fa134caf8bee5d3
    expect(
      fractalPerlin2D(0.5, 0.5, {
        seed: 42,
        amplitudes: [1, 2, 0, 1],
        frequency: 0.25,
      }),
    ).toBe(0.033605902542557374);
  });

  it("should not cross zero at the origin with independent octaves", () => {
    // bfc3b074f0c3e952 — a shared source is zero on its lattice, the origin
    // first; offset octaves are not.
    expect(fractalPerlin3D(0, 0, 0, { seed: "monde" })).toBe(0);
    expect(
      fractalPerlin3D(0, 0, 0, { seed: "monde", independentOctaves: true }),
    ).toBe(-0.15382253414265762);
  });

  it("should keep plain fBm when every weight is one", () => {
    for (const [x, y] of [
      [1.5, 2.5],
      [-7.25, 3.125],
    ]) {
      expect(
        new FractalPerlinNoise2D({ seed: 9, amplitudes: [1, 1, 1] }).noise(
          x,
          y,
        ),
      ).toBe(new FractalPerlinNoise2D({ seed: 9, octaves: 3 }).noise(x, y));
    }
  });

  it("should skip an octave weighted zero", () => {
    // A zero drops the octave from the sum and from the normalisation alike.
    expect(
      new FractalPerlinNoise2D({ seed: 9, amplitudes: [1, 0] }).noise(1.5, 2.5),
    ).toBe(new FractalPerlinNoise2D({ seed: 9, octaves: 1 }).noise(1.5, 2.5));
  });

  it("should stay within [-1, 1]", () => {
    const noise = new FractalPerlinNoise3D({
      seed: 3,
      amplitudes: [1, 1, 2, 2, 2, 1, 1, 1, 1],
      independentOctaves: true,
      frequency: 0.01,
    });
    for (let i = 0; i < 1000; i++) {
      const value = noise.noise(i * 3.7, i * 1.3, i * 2.9);
      expect(value).toBeGreaterThanOrEqual(-1);
      expect(value).toBeLessThanOrEqual(1);
    }
  });

  it("should be deterministic, and differ from the shared field", () => {
    const options = { seed: "det", independentOctaves: true, octaves: 5 };
    const a = new FractalPerlinNoise2D(options).noise(12.3, 45.6);
    const b = new FractalPerlinNoise2D(options).noise(12.3, 45.6);
    expect(a).toBe(b);
    expect(a).not.toBe(
      new FractalPerlinNoise2D({ seed: "det", octaves: 5 }).noise(12.3, 45.6),
    );
  });

  it("should refuse amplitudes it cannot honour", () => {
    for (const amplitudes of [[], [0, 0], [1, NaN], [1, Infinity]]) {
      expect(() => new FractalPerlinNoise2D({ amplitudes })).toThrow(
        RangeError,
      );
    }
  });

  it("should refuse octaves and amplitudes together", () => {
    // `amplitudes` sets the number of octaves: a second count would conflict.
    expect(
      () => new FractalPerlinNoise2D({ amplitudes: [1, 1], octaves: 2 }),
    ).toThrow(RangeError);
  });
});

describe("String seeds", () => {
  // Cross-language conformance vector: also asserted in the Python suite. A
  // string seed is hashed (FNV-1a) to an integer, identically in every package.
  // Exact, for the same reason as the vectors above.
  it("should hash a string seed to a deterministic field", () => {
    // bf8eba3ecad18713
    expect(fractalPerlin2D(0.5, 0.5, { seed: "hello" })).toBe(
      -0.01500367218449442,
    );
  });

  it("should give different fields for different string seeds", () => {
    const a = fractalPerlin2D(1.5, 2.5, { seed: "alpha" });
    const b = fractalPerlin2D(1.5, 2.5, { seed: "beta" });
    expect(a).not.toBe(b);
  });
});
