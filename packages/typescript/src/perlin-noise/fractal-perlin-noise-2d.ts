import { FractalNoiseGenerator } from "../fractal-noise-generator";
import { FractalNoiseGenerator2D } from "../interfaces/fractal-noise-generator-2d";

import { PerlinNoise2D } from "./perlin-noise-2d";
import { FractalPerlinOptions } from "./fractal-perlin-noise-1d";

/**
 * Fractal (multi-octave) 2D Perlin noise: stacks octaves of a {@link PerlinNoise2D}
 * source.
 */
export class FractalPerlinNoise2D
  extends FractalNoiseGenerator
  implements FractalNoiseGenerator2D
{
  private source: PerlinNoise2D;

  constructor(options: FractalPerlinOptions = {}) {
    const { seed, ...fractal } = options;
    super(fractal);
    this.source = new PerlinNoise2D({ seed });
  }

  protected sample(coords: number[]): number {
    return this.source.noise(coords[0], coords[1]);
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

/**
 * One-shot fractal 2D Perlin noise at a given position.
 * Builds a {@link FractalPerlinNoise2D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @returns value in interval [-1, 1]
 */
export function fractalPerlin2D(
  x: number,
  y: number,
  options: FractalPerlinOptions = {},
): number {
  return new FractalPerlinNoise2D(options).noise(x, y);
}
