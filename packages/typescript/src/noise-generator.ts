export interface NoiseGeneratorOptions {
  /** Seed for the noise field; the same seed yields the same field. Defaults to `0`. */
  seed?: number;
}

/**
 * Abstract base for noise generators.
 *
 * Holds the seed that selects the noise field. Concrete algorithms (e.g. Perlin)
 * subclass it and implement a dimension-specific `noise(...)` method — see the
 * `NoiseGenerator{1,2,3}D` interfaces.
 */
export abstract class NoiseGenerator {
  protected seed: number;

  constructor(options: NoiseGeneratorOptions = {}) {
    this.seed = options.seed ?? 0;
  }
}
