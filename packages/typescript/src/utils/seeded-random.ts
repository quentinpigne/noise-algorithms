import { utf8Bytes } from "./utf8";

/**
 * Deterministic xorshift32 PRNG yielding uint32 values.
 *
 * Uses only 32-bit integer operations (masked with `>>> 0`), so it is portable
 * bit-for-bit: the Python package implements the exact same algorithm, which is
 * what lets the same seed produce the same noise field in every language. Do
 * not change this without updating the Python port and the cross-language
 * conformance vectors in both test suites.
 */
export function xorshift32(seed: number): () => number {
  let x = seed >>> 0;
  if (x === 0) x = 0x9e3779b9; // xorshift cannot start from the zero state
  return () => {
    x = (x ^ ((x << 13) >>> 0)) >>> 0;
    x = (x ^ (x >>> 17)) >>> 0;
    x = (x ^ ((x << 5) >>> 0)) >>> 0;
    return x;
  };
}

/**
 * FNV-1a hash of a string's UTF-8 bytes to a uint32, used to turn a string seed
 * into an integer seed.
 *
 * Like {@link xorshift32}, it uses only masked 32-bit integer operations
 * (`Math.imul` + `>>> 0`), so it is bit-for-bit identical to the Python port —
 * the same string seed yields the same field in every language.
 */
export function fnv1a32(text: string): number {
  let hash = 0x811c9dc5;
  for (const byte of utf8Bytes(text)) {
    hash ^= byte;
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}
