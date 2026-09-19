import { NoiseGenerator, NoiseGeneratorOptions } from "../noise-generator";
import { xorshift32 } from "../utils/seeded-random";

/**
 * Abstract class for Perlin noise generators
 * @see https://en.wikipedia.org/wiki/Perlin_noise
 *
 * Produces a single octave of gradient noise. For multi-octave (fractal) noise,
 * use `FractalPerlinNoise{1,2,3}D` or `fractalPerlin{1,2,3}D` from the same
 * entry point.
 *
 * The base owns what every dimension shares: the seeded permutation table and
 * the final scale-and-clamp. The octave itself is **unrolled per dimension** in
 * each subclass — hashing the corners, dotting the gradients and reducing by
 * lerp are written out in scalars rather than driven by a generic hypercube
 * loop.
 *
 * That loop was the readable form, and it cost eleven times the arithmetic it
 * performed: a dimension-agnostic engine has to carry coordinates, offsets and
 * intermediate reductions in arrays, which meant sixteen allocations per call
 * in 3D. The unrolled form keeps **the same operations in the same order**, so
 * the field is unchanged bit-for-bit — the cross-language invariant holds, and
 * the golden vectors are what proves it.
 */
export abstract class PerlinNoise extends NoiseGenerator {
  protected permutation!: number[];

  constructor(options: NoiseGeneratorOptions = {}) {
    super(options);
    this.permutation = this.buildPermutation();
  }

  private buildPermutation(): number[] {
    // Permutation table based on Perlin's original algorithm
    const p: number[] = [];
    for (let i = 0; i < 256; i++) {
      p[i] = i;
    }

    // Seed-based Fisher-Yates shuffle. The PRNG and the integer-modulo index
    // are shared with the Python package, so the same seed yields the same
    // table (and therefore the same field) in every language.
    const random = xorshift32(this.seed);
    for (let i = 255; i > 0; i--) {
      const j = random() % (i + 1);
      [p[i], p[j]] = [p[j], p[i]];
    }

    // Duplication to avoid overflows
    return [...p, ...p];
  }

  /**
   * Scale a raw octave to `[-1, 1]` and clamp it to the documented contract.
   * Shared so every dimension ends its computation the same way.
   */
  protected scaled(raw: number): number {
    return Math.max(-1, Math.min(1, raw * this.normalization));
  }

  /**
   * Multiplier that scales a raw octave to the full `[-1, 1]` range. It is the
   * reciprocal of the gradient set's maximum magnitude, so it is a property of
   * the dimension-specific gradients — see the empirical measurement in
   * `docs/PERLIN_NOISE.md`.
   */
  protected abstract readonly normalization: number;
}
