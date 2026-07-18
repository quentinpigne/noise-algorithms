import { NoiseGenerator3D } from "../interfaces/noise-generator-3d";

export interface VolumeRegion {
  /** Number of samples along x. */
  width: number;
  /** Number of samples along y. */
  height: number;
  /** Number of samples along z. */
  depth: number;
  /** Coordinate of the first sample on x. Defaults to `0`. */
  startX?: number;
  /** Coordinate of the first sample on y. Defaults to `0`. */
  startY?: number;
  /** Coordinate of the first sample on z. Defaults to `0`. */
  startZ?: number;
  /** Coordinate stride between successive samples on all axes. Defaults to `1`. */
  step?: number;
}

/**
 * Sample a 3D noise generator over a regular volume.
 * The sample at `(x, y, z)` is taken at
 * `(startX + x * step, startY + y * step, startZ + z * step)`.
 * @param generator any 3D noise generator (single-octave or fractal)
 * @returns a `depth × height × width` row-major nested array (`volume[z][y][x]`), values in `[-1, 1]`
 */
export function sampleVolume(
  generator: NoiseGenerator3D,
  options: VolumeRegion,
): number[][][] {
  const {
    width,
    height,
    depth,
    startX = 0,
    startY = 0,
    startZ = 0,
    step = 1,
  } = options;
  const volume: number[][][] = [];
  for (let z = 0; z < depth; z++) {
    const plane: number[][] = [];
    for (let y = 0; y < height; y++) {
      const row: number[] = [];
      for (let x = 0; x < width; x++) {
        row.push(
          generator.noise(
            startX + x * step,
            startY + y * step,
            startZ + z * step,
          ),
        );
      }
      plane.push(row);
    }
    volume.push(plane);
  }
  return volume;
}
