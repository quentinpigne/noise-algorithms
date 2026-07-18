import { NoiseGenerator1D } from "./noise-generator-1d";

/**
 * A fractal (multi-octave) 1D noise generator. Like any noise generator it is
 * sampled at a coordinate; the "fractal" part is how it is built (stacking
 * octaves of a source), not its contract.
 */
export interface FractalNoiseGenerator1D extends NoiseGenerator1D {
  noise(x: number): number;
}
