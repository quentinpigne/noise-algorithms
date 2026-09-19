import { UNIT } from "../utils/constants";
import { NoiseGenerator3D } from "../interfaces/noise-generator-3d";
import { NoiseGeneratorOptions } from "../noise-generator";
import { sampleVolume, VolumeRegion } from "../sampling";

import { fade, lerp } from "../utils/interpolation";

import { PerlinNoise } from "./perlin-noise";

// Ken Perlin's improved-noise gradient set: the 12 cube-edge midpoints plus 4
// balanced duplicates (indices 12-15), so a power-of-2 mask `hash & 15` selects
// uniformly with no modulo bias.
const VECTORS_3D = [
  [UNIT, UNIT, 0],
  [-UNIT, UNIT, 0],
  [UNIT, -UNIT, 0],
  [-UNIT, -UNIT, 0],
  [UNIT, 0, UNIT],
  [-UNIT, 0, UNIT],
  [UNIT, 0, -UNIT],
  [-UNIT, 0, -UNIT],
  [0, UNIT, UNIT],
  [0, -UNIT, UNIT],
  [0, UNIT, -UNIT],
  [0, -UNIT, -UNIT],
  [UNIT, UNIT, 0],
  [0, -UNIT, UNIT],
  [-UNIT, UNIT, 0],
  [0, -UNIT, -UNIT],
];

/** The same table, flattened: `GRADIENTS_3D[(hash & 15) * 3 + axis]`. */
const GRADIENTS_3D = Float64Array.from(VECTORS_3D.flat());

/** Dot product of the hashed gradient with the corner displacement. */
function gradient(hash: number, x: number, y: number, z: number): number {
  const i = (hash & 15) * 3;
  return (
    x * GRADIENTS_3D[i] + y * GRADIENTS_3D[i + 1] + z * GRADIENTS_3D[i + 2]
  );
}

export class PerlinNoise3D extends PerlinNoise implements NoiseGenerator3D {
  // The gradients each have a zero component, so 3D noise peaks at ±√2/2
  // (not ±√3/2); ×√2 fills [-1, 1].
  protected readonly normalization = Math.SQRT2;

  /** 3D Gradient : returns the dot product of the gradient vector and the vector from the grid point
   * @param hash hash of the position
   * @param displacement [x, y, z] displacement from the corner
   * @returns gradient value
   */
  protected gradient(hash: number, displacement: number[]): number {
    const [x, y, z] = displacement;
    const vector = VECTORS_3D[hash & 15];
    return x * vector[0] + y * vector[1] + z * vector[2];
  }

  /**
   * Generate a single-octave noise value at a given position
   * @param x position on the x-axis
   * @param y position on the y-axis
   * @param z position on the z-axis
   * @returns value in interval [-1, 1]
   */
  noise(x: number, y: number, z: number): number {
    const p = this.permutation;

    const floorX = Math.floor(x);
    const floorY = Math.floor(y);
    const floorZ = Math.floor(z);

    // Displacements from the low corner, and from the high one a unit away.
    const lowX = x - floorX;
    const lowY = y - floorY;
    const lowZ = z - floorZ;
    const highX = lowX - 1;
    const highY = lowY - 1;
    const highZ = lowZ - 1;

    const u = fade(lowX);
    const v = fade(lowY);
    const w = fade(lowZ);

    const x0 = floorX & 255;
    const y0 = floorY & 255;
    const z0 = floorZ & 255;
    const x1 = (x0 + 1) & 255;
    const y1 = (y0 + 1) & 255;
    const z1 = (z0 + 1) & 255;

    // The permutation folds one axis at a time, so the prefixes are shared:
    // eight corners cost twelve lookups here instead of thirty-two.
    const px0 = p[x0];
    const px1 = p[x1];
    const px0y0 = p[px0 + y0];
    const px0y1 = p[px0 + y1];
    const px1y0 = p[px1 + y0];
    const px1y1 = p[px1 + y1];

    // Interpolate along x, then y, then z — the reduction order the generic
    // engine used, kept so the arithmetic is identical.
    const xy00 = lerp(
      gradient(p[p[px0y0 + z0]], lowX, lowY, lowZ),
      gradient(p[p[px1y0 + z0]], highX, lowY, lowZ),
      u,
    );
    const xy10 = lerp(
      gradient(p[p[px0y1 + z0]], lowX, highY, lowZ),
      gradient(p[p[px1y1 + z0]], highX, highY, lowZ),
      u,
    );
    const xy01 = lerp(
      gradient(p[p[px0y0 + z1]], lowX, lowY, highZ),
      gradient(p[p[px1y0 + z1]], highX, lowY, highZ),
      u,
    );
    const xy11 = lerp(
      gradient(p[p[px0y1 + z1]], lowX, highY, highZ),
      gradient(p[p[px1y1 + z1]], highX, highY, highZ),
      u,
    );

    return this.scaled(lerp(lerp(xy00, xy10, v), lerp(xy01, xy11, v), w));
  }
}

/**
 * One-shot single-octave 3D Perlin noise at a given position.
 * Builds a {@link PerlinNoise3D} per call; reuse an instance for loops.
 * @param x position on the x-axis
 * @param y position on the y-axis
 * @param z position on the z-axis
 * @returns value in interval [-1, 1]
 */
export function perlin3D(
  x: number,
  y: number,
  z: number,
  options: NoiseGeneratorOptions = {},
): number {
  return new PerlinNoise3D(options).noise(x, y, z);
}

/**
 * One-shot single-octave 3D Perlin noise over a regular volume.
 * Builds a {@link PerlinNoise3D} and samples it with {@link sampleVolume}.
 * @returns a `depth × height × width` nested array (`volume[z][y][x]`), values in [-1, 1]
 */
export function perlinVolume(
  options: NoiseGeneratorOptions & VolumeRegion,
): number[][][] {
  const { seed, ...region } = options;
  return sampleVolume(new PerlinNoise3D({ seed }), region);
}
