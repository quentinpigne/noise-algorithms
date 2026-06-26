import { NoiseGenerator1D } from "../interfaces/noise-generator-1d";

import { PerlinNoise } from "./perlin-noise";

export class PerlinNoise1D extends PerlinNoise implements NoiseGenerator1D {
  /** 1D Gradient : keeps or mirrors the displacement depending on the hash
   * @param hash hash of the position
   * @param displacement [x] displacement from the corner
   * @returns gradient value
   */
  protected gradient(hash: number, displacement: number[]): number {
    const [x] = displacement;
    return (hash & 1) === 0 ? x : -x;
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number): number {
    return this.fractal([x]);
  }
}
