import { MAX_INT } from "./utils/constants";

export interface NoiseGeneratorOptions {
  /** Seed for the permutation table; same seed → same field. Defaults to a random seed. */
  seed?: number;
}

export abstract class NoiseGenerator {
  protected seed: number;

  constructor(options: NoiseGeneratorOptions = {}) {
    this.seed = options.seed ?? (Math.random() * MAX_INT) | 0;
  }
}
