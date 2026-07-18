import { FractalNoiseGenerator } from "../fractal-noise-generator";
import { FractalNoiseGenerator3D } from "../interfaces/fractal-noise-generator-3d";
import { sampleVolume, VolumeRegion } from "../sampling";

import { PerlinNoise3D } from "./perlin-noise-3d";
import { FractalPerlinOptions } from "./fractal-perlin-noise-1d";

/**
 * Fractal (multi-octave) 3D Perlin noise: stacks octaves of a {@link PerlinNoise3D}
 * source.
 */
export class FractalPerlinNoise3D
  extends FractalNoiseGenerator
  implements FractalNoiseGenerator3D
{
  private source: PerlinNoise3D;

  constructor(options: FractalPerlinOptions = {}) {
    const { seed, ...fractal } = options;
    super(fractal);
    this.source = new PerlinNoise3D({ seed });
  }

  protected sample(coords: number[]): number {
    return this.source.noise(coords[0], coords[1], coords[2]);
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

/**
 * One-shot fractal 3D Perlin noise at a given position.
 * Builds a {@link FractalPerlinNoise3D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @param z position on the z-axis
 * @returns value in interval [-1, 1]
 */
export function fractalPerlin3D(
  x: number,
  y: number,
  z: number,
  options: FractalPerlinOptions = {},
): number {
  return new FractalPerlinNoise3D(options).noise(x, y, z);
}

/**
 * One-shot fractal 3D Perlin noise over a regular volume.
 * Builds a {@link FractalPerlinNoise3D} and samples it with {@link sampleVolume}.
 * @returns a `depth × height × width` nested array (`volume[z][y][x]`), values in [-1, 1]
 */
export function fractalPerlinVolume(
  options: FractalPerlinOptions & VolumeRegion,
): number[][][] {
  const { width, height, depth, startX, startY, startZ, step, ...generator } =
    options;
  return sampleVolume(new FractalPerlinNoise3D(generator), {
    width,
    height,
    depth,
    startX,
    startY,
    startZ,
    step,
  });
}
