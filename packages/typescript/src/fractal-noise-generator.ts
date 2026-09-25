export interface FractalOptions {
  /**
   * Number of noise layers (octaves) summed together. Defaults to `4`, or to
   * the length of `amplitudes`, which cannot be given with it.
   */
  octaves?: number;
  /** Frequency multiplier between successive octaves. Defaults to `2`. */
  lacunarity?: number;
  /** Amplitude multiplier between successive octaves. Defaults to `0.5`. */
  persistence?: number;
  /** Base frequency applied to the coordinates of the first octave. Defaults to `0.01`. */
  frequency?: number;
  /**
   * Weight of each octave, on top of the persistence curve: octave `i`
   * contributes `amplitudes[i] × persistence^i`. Its length is the number of
   * octaves, so it cannot be given with `octaves`; a zero skips its octave. The
   * weights must be finite, and at least one non-zero. Defaults to a weight of
   * `1` for every octave — plain fBm.
   */
  amplitudes?: readonly number[];
  /**
   * Give every octave its own permutation and its own coordinate offset, drawn
   * from the seed, instead of sampling one source at every frequency.
   *
   * One shared source repeats its lattice at every octave: at the origin, and
   * wherever the octaves' lattices line up, they all cross zero together.
   * Independent octaves decorrelate the layers, which is what a field meant to
   * be read against thresholds wants. Defaults to `false`.
   */
  independentOctaves?: boolean;
}

/**
 * Abstract base for fractal (fBm) noise generators.
 *
 * Fractal noise is not a noise algorithm in itself but a *technique* for
 * stacking octaves of a source noise: each octave samples the source at an
 * increasing frequency and decreasing amplitude, and the contributions are
 * summed and normalised back into the `[-1, 1]` interval.
 *
 * summed and normalised back into the `[-1, 1]` interval. This dimension- and
 * source-agnostic engine lives here; subclasses bind a concrete source and
 * adapt its `noise(...)` signature via `sample`.
 *
 * **The bundled dimensions do not run it.** Passing coordinates as an array
 * means a `map` allocation per octave, and four octaves of 3D noise spent more
 * time allocating than sampling; `FractalPerlinNoise{1,2,3}D` each write their
 * own loop. `fractal` stays as the extension point and as the specification the
 * unrolled loops are tested against.
 */
export abstract class FractalNoiseGenerator {
  protected octaves: number;
  protected lacunarity: number;
  protected persistence: number;
  protected frequency: number;
  /** One weight per octave; all `1` unless `amplitudes` was given. */
  protected weights: readonly number[];
  protected independentOctaves: boolean;
  /**
   * The frequency and amplitude of each octave, and the sum the stacked value
   * is divided by. They do not depend on the coordinates, so the unrolled loops
   * read them instead of recomputing them on every call; they are built with
   * the operations of the generic `fractal` loop, in its order, so they hold
   * the same bits.
   */
  protected octaveFrequencies: Float64Array;
  protected octaveAmplitudes: Float64Array;
  protected amplitudeSum: number;

  constructor(options: FractalOptions = {}) {
    this.weights = weightsOf(options);
    this.octaves = this.weights.length;
    this.lacunarity = options.lacunarity ?? 2;
    this.persistence = options.persistence ?? 0.5;
    this.frequency = options.frequency ?? 0.01;
    this.independentOctaves = options.independentOctaves ?? false;

    this.octaveFrequencies = new Float64Array(this.octaves);
    this.octaveAmplitudes = new Float64Array(this.octaves);
    let amplitude = 1;
    let frequency = this.frequency;
    let amplitudeSum = 0;
    for (let i = 0; i < this.octaves; i++) {
      this.octaveFrequencies[i] = frequency;
      this.octaveAmplitudes[i] = amplitude;
      const weight = this.weights[i];
      if (weight !== 0) amplitudeSum += amplitude * Math.abs(weight);
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }
    this.amplitudeSum = amplitudeSum;
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
      const weight = this.weights[i];
      if (weight !== 0) {
        value +=
          this.sample(
            coords.map((c) => c * frequency),
            i,
          ) *
          amplitude *
          weight;
        maxValue += amplitude * Math.abs(weight);
      }
      amplitude *= this.persistence;
      frequency *= this.lacunarity;
    }

    return value / maxValue;
  }

  /**
   * Sample the wrapped source generator at the given coordinates, for the given
   * octave. Implemented per dimension to bridge the generic coordinate array and
   * the source's `noise(...)` signature; with independent octaves, `octave`
   * selects the source and its offset.
   */
  protected abstract sample(coords: number[], octave: number): number;
}

/**
 * The octave weights an options object asks for.
 *
 * A weight of `1` is exact in floating point, so plain fBm computes the same
 * bits with or without this step.
 */
function weightsOf(options: FractalOptions): readonly number[] {
  const { amplitudes, octaves } = options;
  if (amplitudes === undefined) return new Array<number>(octaves ?? 4).fill(1);

  if (octaves !== undefined) {
    throw new RangeError(
      "give octaves or amplitudes, not both: amplitudes sets the number of octaves",
    );
  }
  if (amplitudes.length === 0) {
    throw new RangeError("amplitudes must name at least one octave");
  }
  if (!amplitudes.every((weight) => Number.isFinite(weight))) {
    throw new RangeError("amplitudes must be finite numbers");
  }
  if (amplitudes.every((weight) => weight === 0)) {
    throw new RangeError("amplitudes must have at least one non-zero weight");
  }
  return [...amplitudes];
}
