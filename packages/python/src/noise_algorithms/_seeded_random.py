"""Deterministic xorshift32 PRNG.

Uses only 32-bit integer operations (masked with ``& 0xFFFFFFFF``), so it is
portable bit-for-bit: the TypeScript package implements the exact same
algorithm, which is what lets the same seed produce the same noise field in
every language. Do not change this without updating the TypeScript port
(``utils/seeded-random.ts``) and the cross-language conformance vectors in both
test suites.
"""

from collections.abc import Callable

_MASK = 0xFFFFFFFF


def xorshift32(seed: int) -> Callable[[], int]:
    """Return a generator function yielding successive ``uint32`` values."""
    x = seed & _MASK
    if x == 0:
        x = 0x9E3779B9  # xorshift cannot start from the zero state

    def next_uint32() -> int:
        nonlocal x
        x ^= (x << 13) & _MASK
        x ^= x >> 17
        x ^= (x << 5) & _MASK
        x &= _MASK
        return x

    return next_uint32
