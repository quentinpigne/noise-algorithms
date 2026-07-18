import { NoiseGenerator, NoiseGeneratorOptions } from "../noise-generator";
import { lerp } from "../utils/interpolation";
import { seededRandom } from "../utils/seeded-random";

/**
 * Abstract class for Perlin noise generators
 * @see https://en.wikipedia.org/wiki/Perlin_noise
 *
 * Produces a single octave of gradient noise. For multi-octave (fractal) noise,
 * use `FractalPerlinNoise{1,2,3}D` or `fractalPerlin{1,2,3}D` from the same
 * entry point.
 *
 * The base implements a dimension-agnostic engine: hashing folds the
 * permutation table over the coordinates, every corner of the surrounding
 * hypercube contributes a gradient dot product, and the contributions are
 * combined by a pairwise lerp reduction along each axis. Subclasses only
 * provide their dimension-specific gradient set via `gradient`.
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

    // Seed-based mix
    const random = seededRandom(this.seed);
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [p[i], p[j]] = [p[j], p[i]];
    }

    // Duplication to avoid overflows
    return [...p, ...p];
  }

  protected fade(t: number): number {
    // Smoothing function 6t^5 - 15t^4 + 10t^3
    return t * t * t * (t * (t * 6 - 15) + 10);
  }

  /**
   * Single octave of N-dimensional Perlin noise at the given coordinates.
   * @param coords position, one entry per dimension
   * @returns noise value in interval [-1, 1]
   */
  protected octave(coords: number[]): number {
    const n = coords.length;

    const floors = coords.map((c) => Math.floor(c));
    const cells = floors.map((f) => f & 255);
    const fracs = coords.map((c, axis) => c - floors[axis]);
    const faded = fracs.map((f) => this.fade(f));

    // Noise contribution of every corner of the surrounding hypercube; the
    // corner index encodes its offsets (bit `axis` = offset along `axis`).
    let values: number[] = [];
    for (let corner = 0; corner < 1 << n; corner++) {
      let h = this.permutation[(cells[0] + (corner & 1)) & 255];
      for (let axis = 1; axis < n; axis++) {
        h =
          this.permutation[h + ((cells[axis] + ((corner >> axis) & 1)) & 255)];
      }
      h = this.permutation[h];

      const displacement = fracs.map((f, axis) => f - ((corner >> axis) & 1));
      values.push(this.gradient(h, displacement));
    }

    // Pairwise lerp reduction along each axis: 2^n -> 2^(n-1) -> ... -> 1.
    for (let axis = 0; axis < n; axis++) {
      const reduced: number[] = [];
      for (let i = 0; i < values.length; i += 2) {
        reduced.push(lerp(values[i], values[i + 1], faded[axis]));
      }
      values = reduced;
    }

    return values[0];
  }

  /**
   * Dot product of the hashed gradient with the corner displacement.
   * Implemented per dimension.
   */
  protected abstract gradient(hash: number, displacement: number[]): number;
}
