/** A 1D noise generator: sampled at a coordinate to produce a value in `[-1, 1]`. */
export interface NoiseGenerator1D {
  noise(x: number): number;
}
