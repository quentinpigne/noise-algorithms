import { describe, expect, it } from "vitest";

import {
  FractalPerlinNoise1D,
  FractalPerlinNoise2D,
  FractalPerlinNoise3D,
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
} from "../src/perlin-noise";

/**
 * The bundled dimensions unroll their octave and their fractal loop for speed,
 * and the generic engines they no longer run stay as the extension point.
 *
 * Two implementations of the same maths is exactly the kind of drift the
 * cross-language invariant cannot survive, so it is pinned here: the fast path
 * must equal the generic one **bit-for-bit**, not merely to a tolerance. A
 * rounding difference is a field difference, and a field difference is a
 * different world from the same seed.
 */

/** Raw bits of a f64: two values that print alike can still differ. */
function bits(value: number): bigint {
  const view = new DataView(new ArrayBuffer(8));
  view.setFloat64(0, value);
  return view.getBigUint64(0);
}

/** Exposes the generic engines, which are `protected`. */
class Generic1D extends PerlinNoise1D {
  generic(x: number): number {
    return this.octave([x]);
  }
}
class Generic2D extends PerlinNoise2D {
  generic(x: number, y: number): number {
    return this.octave([x, y]);
  }
}
class Generic3D extends PerlinNoise3D {
  generic(x: number, y: number, z: number): number {
    return this.octave([x, y, z]);
  }
}
class GenericFractal3D extends FractalPerlinNoise3D {
  generic(x: number, y: number, z: number): number {
    return this.fractal([x, y, z]);
  }
}

const SEEDS = [0, 1, 42, "agreement", "ünïcødé"];

/** Fractional steps, both signs, and the cell borders the fade turns over. */
function coordinates(): number[] {
  const walked = Array.from({ length: 61 }, (_, i) => (i - 30) * 0.37);
  return [...walked, 0, -0, 1, -1, 255, 256, -256, 0.5, -0.5, 1e6];
}

describe("unrolled octave agrees with the generic engine", () => {
  for (const seed of SEEDS) {
    it(`matches in 1D and 2D — seed ${String(seed)}`, () => {
      const one = new Generic1D({ seed });
      const two = new Generic2D({ seed });

      for (const x of coordinates()) {
        expect(bits(one.noise(x))).toBe(bits(one.generic(x)));
        for (const y of coordinates().slice(0, 12)) {
          expect(bits(two.noise(x, y))).toBe(bits(two.generic(x, y)));
        }
      }
    });

    it(`matches in 3D — seed ${String(seed)}`, () => {
      const three = new Generic3D({ seed });

      for (const x of coordinates()) {
        for (const y of coordinates().slice(0, 8)) {
          for (const z of coordinates().slice(0, 5)) {
            expect(bits(three.noise(x, y, z))).toBe(
              bits(three.generic(x, y, z)),
            );
          }
        }
      }
    });
  }

  it("matches for stacked octaves, whatever the fractal settings", () => {
    // Odd counts and non-default lacunarity: the loop must accumulate in the
    // same order, not just reach the same total.
    for (const octaves of [1, 2, 3, 7]) {
      for (const lacunarity of [2, 1.87]) {
        const fractal = new GenericFractal3D({
          seed: "agreement",
          octaves,
          lacunarity,
          persistence: 0.43,
          frequency: 0.017,
        });
        for (const x of coordinates().slice(0, 20)) {
          expect(bits(fractal.noise(x, x * 0.3, x * 0.7))).toBe(
            bits(fractal.generic(x, x * 0.3, x * 0.7)),
          );
        }
      }
    }
  });
});
