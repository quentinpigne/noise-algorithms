import { NoiseGenerator2D } from "../interfaces/noise-generator-2d";

export interface GridRegion {
  /** Number of columns (samples along x). */
  width: number;
  /** Number of rows (samples along y). */
  height: number;
  /** Coordinate of the first column. Defaults to `0`. */
  startX?: number;
  /** Coordinate of the first row. Defaults to `0`. */
  startY?: number;
  /** Coordinate stride between successive samples on both axes. Defaults to `1`. */
  step?: number;
}

/**
 * Sample a 2D noise generator over a regular grid — e.g. an image.
 * The sample at column `x`, row `y` is taken at
 * `(startX + x * step, startY + y * step)`.
 * @param generator any 2D noise generator (single-octave or fractal)
 * @returns a `height × width` row-major nested array (`grid[y][x]`), values in `[-1, 1]`
 */
export function sampleGrid(
  generator: NoiseGenerator2D,
  options: GridRegion,
): number[][] {
  const { width, height, startX = 0, startY = 0, step = 1 } = options;
  const grid: number[][] = [];
  for (let y = 0; y < height; y++) {
    const row: number[] = [];
    for (let x = 0; x < width; x++) {
      row.push(generator.noise(startX + x * step, startY + y * step));
    }
    grid.push(row);
  }
  return grid;
}
