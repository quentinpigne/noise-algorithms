import { UNIT } from "../utils/constants";
import { lerp } from "../utils/interpolation";
import { NoiseGenerator2D } from "../interfaces/noise-generator-2d";

import { PerlinNoise } from "./perlin-noise";

const VECTORS_2D = [
  [UNIT, UNIT],
  [-UNIT, UNIT],
  [UNIT, -UNIT],
  [-UNIT, -UNIT],
  [0, 1],
  [0, -1],
  [1, 0],
  [-1, 0],
];

export class PerlinNoise2D extends PerlinNoise implements NoiseGenerator2D {
  constructor(
    seed?: number,
    scale: number = 0.01,
    octaves: number = 4,
    lacunarity: number = 2,
    persistence: number = 0.5
  ) {
    super(seed, scale, octaves, lacunarity, persistence);
  }

  /** 2D Hash : returns 4 permutations of the permutation table
   * @param x0 position on the x-axis
   * @param x1 position on the x-axis offset by 1
   * @param y0 position on the y-axis
   * @param y1 position on the y-axis offset by 1
   * @returns array of the 4 permutations
   */
  private hash(x0: number, x1: number, y0: number, y1: number): number[] {
    const h0 = this.permutationTable[x0];
    const h1 = this.permutationTable[x1];

    const h00 = this.permutationTable[h0 + y0];
    const h01 = this.permutationTable[h0 + y1];
    const h10 = this.permutationTable[h1 + y0];
    const h11 = this.permutationTable[h1 + y1];

    return [
      this.permutationTable[h00],
      this.permutationTable[h01],
      this.permutationTable[h10],
      this.permutationTable[h11],
    ];
  }

  /** 2D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns gradient value
   */
  private gradient(h: number, x: number, y: number): number {
    return x * VECTORS_2D[h & 7][0] + y * VECTORS_2D[h & 7][1];
  }

  /**
   * Returns the noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns noise value in interval [-1, 1]
   */
  private perlinNoise(x: number, y: number): number {
    // Determine grid cell coordinates
    const x0 = Math.floor(x) & 255;
    const x1 = (x0 + 1) & 255;

    const y0 = Math.floor(y) & 255;
    const y1 = (y0 + 1) & 255;

    // Internal coordinates
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);

    // Fade factors
    const u = this.fade(xf);
    const v = this.fade(yf);

    // 4 hashed gradient indices
    const [h00, h01, h10, h11] = this.hash(x0, x1, y0, y1);

    // Noise components
    const n00 = this.gradient(h00, xf, yf);
    const n01 = this.gradient(h01, xf, yf - 1);
    const n10 = this.gradient(h10, xf - 1, yf);
    const n11 = this.gradient(h11, xf - 1, yf - 1);

    // Combine noises
    const n0 = lerp(n00, n10, u);
    const n1 = lerp(n01, n11, u);
    return lerp(n0, n1, v);
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number): number {
    let value = 0;
    let maxValue = 0;

    let amplitude = 1;
    let frequency = 1;

    for (let i = 0; i < this.octaves; i++) {
      value +=
        this.perlinNoise(
          x * frequency * this.scale,
          y * frequency * this.scale
        ) * amplitude;
      maxValue += amplitude;
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
  }
}
