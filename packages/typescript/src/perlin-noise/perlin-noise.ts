import { NoiseGenerator } from "../noise-generator";
import { seededRandom } from "../utils/seeded-random";

/**
 * Abstract class for Perlin noise generators
 * @see https://en.wikipedia.org/wiki/Perlin_noise
 * It should be implemented for every dimension (1D, 2D, 3D, ...)
 */
export abstract class PerlinNoise extends NoiseGenerator {
  protected scale: number;
  protected octaves: number;
  protected lacunarity: number;
  protected persistence: number;

  protected permutationTable!: number[];

  constructor(
    seed?: number,
    scale: number = 0.01,
    octaves: number = 4,
    lacunarity: number = 2,
    persistence: number = 0.5
  ) {
    super(seed);
    this.scale = scale;
    this.octaves = octaves;
    this.lacunarity = lacunarity;
    this.persistence = persistence;
    this.initPermutationTable();
  }

  private initPermutationTable(): void {
    // Permutation table based on Perlin's original algorithm
    const p: number[] = [];
    for (let i = 0; i < 256; i++) {
      p[i] = i;
    }

    // Seed-based mix
    const random = seededRandom(this.seed);
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [p[i], p[j]] = [p[j], p[i]];
    }

    // Duplication to avoid overflows
    this.permutationTable = [...p, ...p];
  }

  protected fade(t: number): number {
    // Smoothing function 6t^5 - 15t^4 + 10t^3
    return t * t * t * (t * (t * 6 - 15) + 10);
  }
}
