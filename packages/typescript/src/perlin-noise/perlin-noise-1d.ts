import { lerp } from "../utils/interpolation";
import { NoiseGenerator1D } from "../interfaces/noise-generator-1d";

import { PerlinNoise } from "./perlin-noise";

export class PerlinNoise1D extends PerlinNoise implements NoiseGenerator1D {
  constructor(
    seed?: number,
    scale: number = 0.01,
    octaves: number = 4,
    lacunarity: number = 2,
    persistence: number = 0.5
  ) {
    super(seed, scale, octaves, lacunarity, persistence);
  }

  /** 1D Hash : returns 2 permutations of the permutation table
   * @param x0 position on the x-axis
   * @param x1 position on the x-axis offset by 1
   * @returns array of the 2 permutations
   */
  private hash(x0: number, x1: number): number[] {
    const h0 = this.permutationTable[x0];
    const h1 = this.permutationTable[x1];

    return [this.permutationTable[h0], this.permutationTable[h1]];
  }

  /** 1D Gradient : returns +x or -x depending on the permutation
   * @param hash hash of the position
   * @param x position on the x-axis
   * @returns gradient value
   */
  private gradient(hash: number, x: number): number {
    return (hash & 1) === 0 ? x : -x;
  }

  /**
   * Returns the noise value at a given position
   * @param x position on the x-axis
   * @returns noise value in interval [-1, 1]
   */
  private perlinNoise(x: number): number {
    // Determine axis coordinates
    const x0 = Math.floor(x) & 255;
    const x1 = (x0 + 1) & 255;

    // Internal coordinate (fractional part)
    const xf = x - Math.floor(x);

    // Fade factor
    const u = this.fade(xf);

    // 2 hashed gradient indices
    const [h0, h1] = this.hash(x0, x1);

    // Noise components
    const n0 = this.gradient(h0, xf);
    const n1 = this.gradient(h1, xf - 1);

    return lerp(n0, n1, u);
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number): number {
    let value = 0;
    let maxValue = 0;

    let amplitude = 1;
    let frequency = 1;

    for (let i = 0; i < this.octaves; i++) {
      value += this.perlinNoise(x * frequency * this.scale) * amplitude;
      maxValue += amplitude;
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
  }
}
