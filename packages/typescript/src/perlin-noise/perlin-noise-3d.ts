import { UNIT } from "../utils/constants";
import { lerp } from "../utils/interpolation";
import { NoiseGenerator3D } from "../interfaces/noise-generator-3d";

import { PerlinNoise } from "./perlin-noise";

const VECTORS_3D = [
  [UNIT, UNIT, 0],
  [UNIT, -UNIT, 0],
  [-UNIT, UNIT, 0],
  [-UNIT, -UNIT, 0],
  [UNIT, 0, UNIT],
  [UNIT, 0, -UNIT],
  [-UNIT, 0, UNIT],
  [-UNIT, 0, -UNIT],
  [0, UNIT, UNIT],
  [0, UNIT, -UNIT],
  [0, -UNIT, UNIT],
  [0, -UNIT, -UNIT],
];

export class PerlinNoise3D extends PerlinNoise implements NoiseGenerator3D {
  constructor(
    seed?: number,
    scale: number = 0.01,
    octaves: number = 4,
    lacunarity: number = 2,
    persistence: number = 0.5
  ) {
    super(seed, scale, octaves, lacunarity, persistence);
  }

  /** 3D Hash : returns 8 permutations of the permutation table
   * @param x0 position on the x-axis
   * @param x1 position on the x-axis offset by 1
   * @param y0 position on the y-axis
   * @param y1 position on the y-axis offset by 1
   * @param z0 position on the y-axis
   * @param z1 position on the y-axis offset by 1
   * @returns array of the 8 permutations
   */
  private hash(
    x0: number,
    x1: number,
    y0: number,
    y1: number,
    z0: number,
    z1: number
  ): number[] {
    const h0 = this.permutationTable[x0];
    const h1 = this.permutationTable[x1];

    const h00 = this.permutationTable[h0 + y0];
    const h01 = this.permutationTable[h0 + y1];
    const h10 = this.permutationTable[h1 + y0];
    const h11 = this.permutationTable[h1 + y1];

    const h000 = this.permutationTable[h00 + z0];
    const h001 = this.permutationTable[h00 + z1];
    const h010 = this.permutationTable[h01 + z0];
    const h011 = this.permutationTable[h01 + z1];
    const h100 = this.permutationTable[h10 + z0];
    const h101 = this.permutationTable[h10 + z1];
    const h110 = this.permutationTable[h11 + z0];
    const h111 = this.permutationTable[h11 + z1];

    return [
      this.permutationTable[h000],
      this.permutationTable[h001],
      this.permutationTable[h010],
      this.permutationTable[h011],
      this.permutationTable[h100],
      this.permutationTable[h101],
      this.permutationTable[h110],
      this.permutationTable[h111],
    ];
  }

  /** 3D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @param z position on the z-axis
   * @returns gradient value
   */
  private gradient(h: number, x: number, y: number, z: number): number {
    return (
      x * VECTORS_3D[h & 11][0] +
      y * VECTORS_3D[h & 11][1] +
      z * VECTORS_3D[h & 11][2]
    );
  }

  /**
   * Returns the noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @param z position on the z-axis
   * @returns noise value in interval [-1, 1]
   */
  private perlinNoise(x: number, y: number, z: number): number {
    // Determine grid cell coordinates
    const x0 = Math.floor(x) & 255;
    const x1 = (x0 + 1) & 255;

    const y0 = Math.floor(y) & 255;
    const y1 = (y0 + 1) & 255;

    const z0 = Math.floor(z) & 255;
    const z1 = (z0 + 1) & 255;

    // Internal coordinates
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);
    const zf = z - Math.floor(z);

    // Fade factors
    const u = this.fade(xf);
    const v = this.fade(yf);
    const w = this.fade(zf);

    // 4 hashed gradient indices
    const [h000, h001, h010, h011, h100, h101, h110, h111] = this.hash(
      x0,
      x1,
      y0,
      y1,
      z0,
      z1
    );

    // Noise components
    const n000 = this.gradient(h000, xf, yf, zf);
    const n001 = this.gradient(h001, xf, yf, zf - 1);
    const n010 = this.gradient(h010, xf, yf - 1, zf);
    const n011 = this.gradient(h011, xf, yf - 1, zf - 1);
    const n100 = this.gradient(h100, xf - 1, yf, zf);
    const n101 = this.gradient(h101, xf - 1, yf, zf - 1);
    const n110 = this.gradient(h110, xf - 1, yf - 1, zf);
    const n111 = this.gradient(h111, xf - 1, yf - 1, zf - 1);

    // Combine noises
    const n00 = lerp(n000, n100, u);
    const n01 = lerp(n001, n101, u);
    const n10 = lerp(n010, n110, u);
    const n11 = lerp(n011, n111, u);

    const n0 = lerp(n00, n10, v);
    const n1 = lerp(n01, n11, v);

    return lerp(n0, n1, w);
  }

  noise(x: number, y: number, z: number): number {
    let value = 0;
    let maxValue = 0;

    let amplitude = 1;
    let frequency = 1;

    for (let i = 0; i < this.octaves; i++) {
      value +=
        this.perlinNoise(
          x * frequency * this.scale,
          y * frequency * this.scale,
          z * frequency * this.scale
        ) * amplitude;
      maxValue += amplitude;
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
  }
}
