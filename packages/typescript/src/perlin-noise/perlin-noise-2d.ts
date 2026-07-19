import { UNIT } from "../utils/constants";
import { NoiseGenerator2D } from "../interfaces/noise-generator-2d";
import { NoiseGeneratorOptions } from "../noise-generator";
import { sampleGrid, GridRegion } from "../sampling";

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
  // Raw 2D gradient noise peaks at ±√2/2, so ×√2 fills [-1, 1].
  protected readonly normalization = Math.SQRT2;

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
   * Generate a single-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number): number {
    return this.octave([x, y]);
  }
}

/**
 * One-shot single-octave 2D Perlin noise at a given position.
 * Builds a {@link PerlinNoise2D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @returns value in interval [-1, 1]
 */
export function perlin2D(
  x: number,
  y: number,
  options: NoiseGeneratorOptions = {},
): number {
  return new PerlinNoise2D(options).noise(x, y);
}

/**
 * One-shot single-octave 2D Perlin noise over a regular grid — e.g. an image.
 * Builds a {@link PerlinNoise2D} and samples it with {@link sampleGrid}.
 * @returns a `height × width` nested array (`grid[y][x]`), values in [-1, 1]
 */
export function perlinGrid(
  options: NoiseGeneratorOptions & GridRegion,
): number[][] {
  const { seed, ...region } = options;
  return sampleGrid(new PerlinNoise2D({ seed }), region);
}
