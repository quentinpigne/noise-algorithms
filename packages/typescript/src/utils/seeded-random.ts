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
