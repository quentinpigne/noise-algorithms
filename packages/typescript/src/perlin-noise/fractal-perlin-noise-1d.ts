import {
  FractalNoiseGenerator,
  FractalOptions,
} from "../fractal-noise-generator";
import { NoiseGeneratorOptions } from "../noise-generator";
import { FractalNoiseGenerator1D } from "../interfaces/fractal-noise-generator-1d";
import { sampleLine, LineRegion } from "../sampling";
import { OFFSET_AXES, octaveSources } from "../octave-sources";

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
  /** The source of each octave: one shared, or one each when independent. */
  private sources: readonly PerlinNoise1D[];
  private offsets: Float64Array;

  constructor(options: FractalPerlinOptions = {}) {
    const { seed, ...fractal } = options;
    super(fractal);
    const built = octaveSources(
      seed,
      this.octaves,
      this.independentOctaves,
      (octaveSeed) => new PerlinNoise1D({ seed: octaveSeed }),
    );
    this.sources = built.sources;
    this.offsets = built.offsets;
  }

  /**
   * Bridges the generic `fractal` engine to the source's signature.
   *
   * With independent octaves, `octave` selects the source and its offset; a
   * shared source is sampled as is, so plain fBm keeps its exact bits.
   *
   * **Feeds the generic `fractal` only.** `noise` stacks its own octaves, so
   * overriding this method does *not* change what `noise` returns. To stack a
   * different source, extend {@link FractalNoiseGenerator} directly and
   * implement `noise` alongside `sample`.
   */
  protected sample(coords: number[], octave: number): number {
    const source = this.sources[octave];
    if (!this.independentOctaves) return source.noise(coords[0]);
    const at = octave * OFFSET_AXES;
    return source.noise(coords[0] + this.offsets[at]);
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number): number {
    if (this.independentOctaves) return this.independentNoise(x);

    // Plain fBm, inlined: one source, sampled at every frequency.
    const source = this.sources[0];
    let value = 0;

    for (let i = 0; i < this.octaves; i++) {
      const weight = this.weights[i];
      if (weight !== 0) {
        const frequency = this.octaveFrequencies[i];
        value +=
          source.noise(x * frequency) * this.octaveAmplitudes[i] * weight;
      }
    }

    return value / this.amplitudeSum;
  }

  /** Each octave samples its own source, from its own offset. */
  private independentNoise(x: number): number {
    let value = 0;

    for (let i = 0; i < this.octaves; i++) {
      const weight = this.weights[i];
      if (weight !== 0) {
        const frequency = this.octaveFrequencies[i];
        const at = i * OFFSET_AXES;
        value +=
          this.sources[i].noise(x * frequency + this.offsets[at]) *
          this.octaveAmplitudes[i] *
          weight;
      }
    }

    return value / this.amplitudeSum;
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
