import {
  FractalNoiseGenerator,
  FractalOptions,
} from "../fractal-noise-generator";
import { NoiseGeneratorOptions } from "../noise-generator";
import { FractalNoiseGenerator1D } from "../interfaces/fractal-noise-generator-1d";
import { sampleLine, LineRegion } from "../sampling";

import { PerlinNoise1D } from "./perlin-noise-1d";

/** Options for fractal Perlin noise: a seed for the source plus the fractal layering options. */
export type FractalPerlinOptions = NoiseGeneratorOptions & FractalOptions;

/**
 * Fractal (multi-octave) 1D Perlin noise: stacks octaves of a {@link PerlinNoise1D}
 * source.
 */
export class FractalPerlinNoise1D
  extends FractalNoiseGenerator
  implements FractalNoiseGenerator1D
{
  private source: PerlinNoise1D;

  constructor(options: FractalPerlinOptions = {}) {
    const { seed, ...fractal } = options;
    super(fractal);
    this.source = new PerlinNoise1D({ seed });
  }

  protected sample(coords: number[]): number {
    return this.source.noise(coords[0]);
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

/**
 * One-shot fractal 1D Perlin noise at a given position.
 * Builds a {@link FractalPerlinNoise1D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @returns value in interval [-1, 1]
 */
export function fractalPerlin1D(
  x: number,
  options: FractalPerlinOptions = {},
): number {
  return new FractalPerlinNoise1D(options).noise(x);
}

/**
 * One-shot fractal 1D Perlin noise over a regular interval — e.g. a curve.
 * Builds a {@link FractalPerlinNoise1D} and samples it with {@link sampleLine}.
 * @returns an array of `count` values, each in [-1, 1]
 */
export function fractalPerlinLine(
  options: FractalPerlinOptions & LineRegion,
): number[] {
  const { count, start, step, ...generator } = options;
  return sampleLine(new FractalPerlinNoise1D(generator), {
    count,
    start,
    step,
  });
}
