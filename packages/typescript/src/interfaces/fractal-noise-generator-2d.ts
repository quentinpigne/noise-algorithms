import { NoiseGenerator2D } from "./noise-generator-2d";

/**
 * A fractal (multi-octave) 2D noise generator. Like any noise generator it is
 * sampled at a coordinate; the "fractal" part is how it is built (stacking
 * octaves of a source), not its contract.
 */
export interface FractalNoiseGenerator2D extends NoiseGenerator2D {
  noise(x: number, y: number): number;
}
