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

  /**
   * Bridges the generic `fractal` engine to the source's signature.
   *
   * **Feeds the generic `fractal` only.** `noise` stacks its own octaves, so
   * overriding this method does *not* change what `noise` returns. To stack a
   * different source, extend {@link FractalNoiseGenerator} directly and
   * implement `noise` alongside `sample`.
   */
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
    let value = 0;
    let maxValue = 0;
    let amplitude = 1;
    let frequency = this.frequency;

    for (let i = 0; i < this.octaves; i++) {
      value +=
        this.source.noise(x * frequency, y * frequency, z * frequency) *
        amplitude;
      maxValue += amplitude;
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
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
