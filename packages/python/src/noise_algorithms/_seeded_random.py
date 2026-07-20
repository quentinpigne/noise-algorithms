"""Deterministic 32-bit seeding primitives (xorshift32 PRNG + FNV-1a hash).

Both use only 32-bit integer operations (masked with ``& 0xFFFFFFFF``), so they
are portable bit-for-bit: the TypeScript package implements the exact same
algorithms, which is what lets the same seed produce the same noise field in
every language. Do not change these without updating the TypeScript port
(``utils/seeded-random.ts``) and the cross-language conformance vectors in both
test suites.
"""

from collections.abc import Callable

_MASK = 0xFFFFFFFF


def fnv1a32(text: str) -> int:
    """FNV-1a hash of a string's UTF-8 bytes to a ``uint32``.

    Used to turn a string seed into an integer seed.
    """
    hash_ = 0x811C9DC5
    for byte in text.encode("utf-8"):
        hash_ ^= byte
        hash_ = (hash_ * 0x01000193) & _MASK
    return hash_


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
