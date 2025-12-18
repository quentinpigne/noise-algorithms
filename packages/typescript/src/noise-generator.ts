import { MAX_INT } from "./utils/constants";

export abstract class NoiseGenerator {
  protected seed: number;

  constructor(seed?: number) {
    this.seed = seed || (Math.random() * MAX_INT) | 0;
  }
}
