import { UNIT } from "../utils/constants";
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
  /** 2D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param displacement [x, y] displacement from the corner
   * @returns gradient value
   */
  protected gradient(hash: number, displacement: number[]): number {
    const [x, y] = displacement;
    return x * VECTORS_2D[hash & 7][0] + y * VECTORS_2D[hash & 7][1];
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number): number {
    return this.fractal([x, y]);
  }
}
