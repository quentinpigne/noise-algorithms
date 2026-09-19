export interface FractalOptions {
  /** Number of noise layers (octaves) summed together. Defaults to `4`. */
  octaves?: number;
  /** Frequency multiplier between successive octaves. Defaults to `2`. */
  lacunarity?: number;
  /** Amplitude multiplier between successive octaves. Defaults to `0.5`. */
  persistence?: number;
  /** Base frequency applied to the coordinates of the first octave. Defaults to `0.01`. */
  frequency?: number;
}

/**
 * Abstract base for fractal (fBm) noise generators.
 *
 * Fractal noise is not a noise algorithm in itself but a *technique* for
 * stacking octaves of a source noise: each octave samples the source at an
 * increasing frequency and decreasing amplitude, and the contributions are
 * summed and normalised back into the `[-1, 1]` interval.
 *
 * The settings live here; the stacking loop is **written out per dimension** in
 * each subclass. A source-agnostic loop has to pass coordinates as an array and
 * scale them with a `map`, which allocates once per octave — four octaves of 3D
 * noise spent more time allocating than sampling. The unrolled loops keep the
 * same operations in the same order, so the field is unchanged bit-for-bit.
 */
export abstract class FractalNoiseGenerator {
  protected octaves: number;
  protected lacunarity: number;
  protected persistence: number;
  protected frequency: number;

  constructor(options: FractalOptions = {}) {
    this.octaves = options.octaves ?? 4;
    this.lacunarity = options.lacunarity ?? 2;
    this.persistence = options.persistence ?? 0.5;
    this.frequency = options.frequency ?? 0.01;
  }
}
