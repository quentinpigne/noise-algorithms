import { UNIT } from "../utils/constants";
import { NoiseGenerator3D } from "../interfaces/noise-generator-3d";
import { NoiseGeneratorOptions } from "../noise-generator";
import { sampleVolume, VolumeRegion } from "../sampling";

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
   * Generate a single-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @param z position on the z-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number, z: number): number {
    return this.octave([x, y, z]);
  }
}

/**
 * One-shot single-octave 3D Perlin noise at a given position.
 * Builds a {@link PerlinNoise3D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @param z position on the z-axis
 * @returns value in interval [-1, 1]
 */
export function perlin3D(
  x: number,
  y: number,
  z: number,
  options: NoiseGeneratorOptions = {},
): number {
  return new PerlinNoise3D(options).noise(x, y, z);
}

/**
 * One-shot single-octave 3D Perlin noise over a regular volume.
 * Builds a {@link PerlinNoise3D} and samples it with {@link sampleVolume}.
 * @returns a `depth × height × width` nested array (`volume[z][y][x]`), values in [-1, 1]
 */
export function perlinVolume(
  options: NoiseGeneratorOptions & VolumeRegion,
): number[][][] {
  const { seed, ...region } = options;
  return sampleVolume(new PerlinNoise3D({ seed }), region);
}
