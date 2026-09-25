import { FractalNoiseGenerator } from "../fractal-noise-generator";
import { FractalNoiseGenerator2D } from "../interfaces/fractal-noise-generator-2d";
import { sampleGrid, GridRegion } from "../sampling";
import { OFFSET_AXES, octaveSources } from "../octave-sources";

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
  /** The source of each octave: one shared, or one each when independent. */
  private sources: readonly PerlinNoise2D[];
  private offsets: Float64Array;

  constructor(options: FractalPerlinOptions = {}) {
    const { seed, ...fractal } = options;
    super(fractal);
    const built = octaveSources(
      seed,
      this.octaves,
      this.independentOctaves,
      (octaveSeed) => new PerlinNoise2D({ seed: octaveSeed }),
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
    if (!this.independentOctaves) return source.noise(coords[0], coords[1]);
    const at = octave * OFFSET_AXES;
    return source.noise(
      coords[0] + this.offsets[at],
      coords[1] + this.offsets[at + 1],
    );
  }

  /**
   * Generate a multi-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number): number {
    if (this.independentOctaves) return this.independentNoise(x, y);

    // Plain fBm, inlined: one source, sampled at every frequency.
    const source = this.sources[0];
    let value = 0;

    for (let i = 0; i < this.octaves; i++) {
      const weight = this.weights[i];
      if (weight !== 0) {
        const frequency = this.octaveFrequencies[i];
        value +=
          source.noise(x * frequency, y * frequency) *
          this.octaveAmplitudes[i] *
          weight;
      }
    }

    return value / this.amplitudeSum;
  }

  /** Each octave samples its own source, from its own offset. */
  private independentNoise(x: number, y: number): number {
    let value = 0;

    for (let i = 0; i < this.octaves; i++) {
      const weight = this.weights[i];
      if (weight !== 0) {
        const frequency = this.octaveFrequencies[i];
        const at = i * OFFSET_AXES;
        value +=
          this.sources[i].noise(
            x * frequency + this.offsets[at],
            y * frequency + this.offsets[at + 1],
          ) *
          this.octaveAmplitudes[i] *
          weight;
      }
    }

    return value / this.amplitudeSum;
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

/**
 * One-shot fractal 2D Perlin noise over a regular grid — e.g. an image.
 * Builds a {@link FractalPerlinNoise2D} and samples it with {@link sampleGrid}.
 * @returns a `height × width` nested array (`grid[y][x]`), values in [-1, 1]
 */
export function fractalPerlinGrid(
  options: FractalPerlinOptions & GridRegion,
): number[][] {
  const { width, height, startX, startY, step, ...generator } = options;
  return sampleGrid(new FractalPerlinNoise2D(generator), {
    width,
    height,
    startX,
    startY,
    step,
  });
}
