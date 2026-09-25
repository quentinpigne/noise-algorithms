import { resolveSeed } from "./noise-generator";
import { xorshift32 } from "./utils/seeded-random";

/** A coordinate offset spans one period of the permutation lattice. */
const OFFSET_RANGE = 256;

/** `2^32`: turns a uint32 draw into `[0, 1)`, exactly. */
const UINT32_RANGE = 4294967296;

/** Offsets drawn per octave, whatever the dimension: x, y, then z. */
export const OFFSET_AXES = 3;

/** The source each octave samples, and where it samples it from. */
export interface OctaveSources<T> {
  readonly sources: readonly T[];
  /** `OFFSET_AXES` per octave; all zero for a shared source. */
  readonly offsets: Float64Array;
}

/**
 * Build the sources of a fractal generator's octaves.
 *
 * Shared, every octave samples one source built from the seed — plain fBm.
 *
 * Independent, the seed drives an xorshift32 stream: for each octave in turn,
 * one draw seeds its source, then three draws give its x, y and z offsets in
 * `[0, 256)`. Three offsets are drawn in every dimension, so a 2D generator
 * reads the same stream as a 3D one and simply leaves z unused. This order is
 * part of the cross-language invariant: the Python package draws the same
 * values in the same order.
 */
export function octaveSources<T>(
  seed: number | string | undefined,
  count: number,
  independent: boolean,
  make: (seed: number) => T,
): OctaveSources<T> {
  const offsets = new Float64Array(count * OFFSET_AXES);
  if (!independent) {
    const shared = make(resolveSeed(seed));
    return { sources: new Array<T>(count).fill(shared), offsets };
  }

  const random = xorshift32(resolveSeed(seed));
  const sources: T[] = [];
  for (let octave = 0; octave < count; octave++) {
    sources.push(make(random()));
    for (let axis = 0; axis < OFFSET_AXES; axis++) {
      offsets[octave * OFFSET_AXES + axis] =
        (random() / UINT32_RANGE) * OFFSET_RANGE;
    }
  }
  return { sources, offsets };
}
