import { UNIT } from "../utils/constants";
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
  /** 3D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param displacement [x, y, z] displacement from the corner
   * @returns gradient value
   */
  protected gradient(hash: number, displacement: number[]): number {
    const [x, y, z] = displacement;
    const vector = VECTORS_3D[hash % 12];
    return x * vector[0] + y * vector[1] + z * vector[2];
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @param z position on the z-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number, z: number): number {
    return this.fractal([x, y, z]);
  }
}
