import { NoiseGenerator1D } from "../interfaces/noise-generator-1d";

export interface LineRegion {
  /** Number of samples to take. */
  count: number;
  /** Coordinate of the first sample. Defaults to `0`. */
  start?: number;
  /** Coordinate stride between successive samples. Defaults to `1`. */
  step?: number;
}

/**
 * Sample a 1D noise generator over a regular interval — e.g. a curve.
 * The i-th sample is taken at `start + i * step`.
 * @param generator any 1D noise generator (single-octave or fractal)
 * @returns an array of `count` values, each in `[-1, 1]`
 */
export function sampleLine(
  generator: NoiseGenerator1D,
  options: LineRegion,
): number[] {
  const { count, start = 0, step = 1 } = options;
  const values: number[] = [];
  for (let i = 0; i < count; i++) {
    values.push(generator.noise(start + i * step));
  }
  return values;
}
