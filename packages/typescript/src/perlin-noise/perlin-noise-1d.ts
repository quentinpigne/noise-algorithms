import { NoiseGenerator1D } from "../interfaces/noise-generator-1d";
import { NoiseGeneratorOptions } from "../noise-generator";
import { sampleLine, LineRegion } from "../sampling";

import { PerlinNoise } from "./perlin-noise";

export class PerlinNoise1D extends PerlinNoise implements NoiseGenerator1D {
  // Raw 1D gradient noise peaks at ±0.5, so ×2 fills [-1, 1].
  protected readonly normalization = 2;

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
   * Generate a single-octave noise value at a given position
   * @param x position on the x-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number): number {
    return this.octave([x]);
  }
}

/**
 * One-shot single-octave 1D Perlin noise at a given position.
 * Builds a {@link PerlinNoise1D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @returns value in interval [-1, 1]
 */
export function perlin1D(
  x: number,
  options: NoiseGeneratorOptions = {},
): number {
  return new PerlinNoise1D(options).noise(x);
}

/**
 * One-shot single-octave 1D Perlin noise over a regular interval — e.g. a curve.
 * Builds a {@link PerlinNoise1D} and samples it with {@link sampleLine}.
 * @returns an array of `count` values, each in [-1, 1]
 */
export function perlinLine(
  options: NoiseGeneratorOptions & LineRegion,
): number[] {
  const { seed, ...region } = options;
  return sampleLine(new PerlinNoise1D({ seed }), region);
}
