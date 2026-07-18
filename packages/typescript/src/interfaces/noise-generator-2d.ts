/** A 2D noise generator: sampled at a coordinate to produce a value in `[-1, 1]`. */
export interface NoiseGenerator2D {
  noise(x: number, y: number): number;
}
