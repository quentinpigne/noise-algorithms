/** A 3D noise generator: sampled at a coordinate to produce a value in `[-1, 1]`. */
export interface NoiseGenerator3D {
  noise(x: number, y: number, z: number): number;
}
