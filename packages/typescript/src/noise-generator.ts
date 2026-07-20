import { fnv1a32 } from "./utils/seeded-random";

export interface NoiseGeneratorOptions {
  /**
   * Seed for the noise field; the same seed yields the same field. A string is
   * hashed to an integer, so named seeds (e.g. `"my-world"`) work too. Defaults
   * to `0`.
   */
  seed?: number | string;
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
    const seed = options.seed ?? 0;
    this.seed = typeof seed === "string" ? fnv1a32(seed) : seed;
  }
}
