import { NoiseGenerator3D } from "./noise-generator-3d";

/**
 * A fractal (multi-octave) 3D noise generator. Like any noise generator it is
 * sampled at a coordinate; the "fractal" part is how it is built (stacking
 * octaves of a source), not its contract.
 */
export interface FractalNoiseGenerator3D extends NoiseGenerator3D {
  noise(x: number, y: number, z: number): number;
}
