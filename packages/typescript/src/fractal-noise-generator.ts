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
 * summed and normalised back into the `[-1, 1]` interval. This dimension- and
 * source-agnostic engine lives here; subclasses bind a concrete source and
 * adapt its `noise(...)` signature via `sample`.
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

  /**
   * Sum `octaves` layers of the source noise at the given coordinates.
   * @param coords position, one entry per dimension
   * @returns value in interval [-1, 1]
   */
  protected fractal(coords: number[]): number {
    let value = 0;
    let maxValue = 0;

    let amplitude = 1;
    let frequency = this.frequency;

    for (let i = 0; i < this.octaves; i++) {
      value += this.sample(coords.map((c) => c * frequency)) * amplitude;
      maxValue += amplitude;
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
  }

  /**
   * Sample the wrapped source generator at the given coordinates.
   * Implemented per dimension to bridge the generic coordinate array and the
   * source's `noise(...)` signature.
   */
  protected abstract sample(coords: number[]): number;
}
