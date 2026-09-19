import { UNIT } from "../utils/constants";
import { NoiseGenerator2D } from "../interfaces/noise-generator-2d";
import { NoiseGeneratorOptions } from "../noise-generator";
import { sampleGrid, GridRegion } from "../sampling";

import { fade, lerp } from "../utils/interpolation";

import { PerlinNoise } from "./perlin-noise";

const VECTORS_2D = [
  [UNIT, UNIT],
  [-UNIT, UNIT],
  [UNIT, -UNIT],
  [-UNIT, -UNIT],
  [0, 1],
  [0, -1],
  [1, 0],
  [-1, 0],
];

/** The same table, flattened: `GRADIENTS_2D[(hash & 7) * 2 + axis]`. */
const GRADIENTS_2D = Float64Array.from(VECTORS_2D.flat());

/** Dot product of the hashed gradient with the corner displacement. */
function gradient(hash: number, x: number, y: number): number {
  const i = (hash & 7) * 2;
  return x * GRADIENTS_2D[i] + y * GRADIENTS_2D[i + 1];
}

export class PerlinNoise2D extends PerlinNoise implements NoiseGenerator2D {
  // Raw 2D gradient noise peaks at ±√2/2, so ×√2 fills [-1, 1].
  protected readonly normalization = Math.SQRT2;

  /** 2D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param displacement [x, y] displacement from the corner
   * @returns gradient value
   */
  protected gradient(hash: number, displacement: number[]): number {
    const [x, y] = displacement;
    return x * VECTORS_2D[hash & 7][0] + y * VECTORS_2D[hash & 7][1];
  }

  /**
   * Generate a single-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number): number {
    const p = this.permutation;

    const floorX = Math.floor(x);
    const floorY = Math.floor(y);

    const lowX = x - floorX;
    const lowY = y - floorY;
    const highX = lowX - 1;
    const highY = lowY - 1;

    const u = fade(lowX);
    const v = fade(lowY);

    const x0 = floorX & 255;
    const y0 = floorY & 255;
    const x1 = (x0 + 1) & 255;
    const y1 = (y0 + 1) & 255;

    const px0 = p[x0];
    const px1 = p[x1];

    // Interpolate along x, then y — the reduction order of the generic engine.
    const y0Row = lerp(
      gradient(p[p[px0 + y0]], lowX, lowY),
      gradient(p[p[px1 + y0]], highX, lowY),
      u,
    );
    const y1Row = lerp(
      gradient(p[p[px0 + y1]], lowX, highY),
      gradient(p[p[px1 + y1]], highX, highY),
      u,
    );

    return this.scaled(lerp(y0Row, y1Row, v));
  }
}

/**
 * One-shot single-octave 2D Perlin noise at a given position.
 * Builds a {@link PerlinNoise2D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @returns value in interval [-1, 1]
 */
export function perlin2D(
  x: number,
  y: number,
  options: NoiseGeneratorOptions = {},
): number {
  return new PerlinNoise2D(options).noise(x, y);
}

/**
 * One-shot single-octave 2D Perlin noise over a regular grid — e.g. an image.
 * Builds a {@link PerlinNoise2D} and samples it with {@link sampleGrid}.
 * @returns a `height × width` nested array (`grid[y][x]`), values in [-1, 1]
 */
export function perlinGrid(
  options: NoiseGeneratorOptions & GridRegion,
): number[][] {
  const { seed, ...region } = options;
  return sampleGrid(new PerlinNoise2D({ seed }), region);
}
