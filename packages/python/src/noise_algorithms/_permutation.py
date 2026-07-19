"""Seeded permutation table used to hash grid coordinates.

The table is built with a Fisher-Yates shuffle driven by the portable
:func:`~noise_algorithms._seeded_random.xorshift32` PRNG. That PRNG and the
integer-modulo index are shared with the TypeScript package, so the same seed
yields the same table — and therefore the same field — in every language. Each
noise generator builds its table once in its constructor and holds it for its
lifetime.
"""

from ._seeded_random import xorshift32


def build_permutation(seed: int) -> tuple[int, ...]:
    """Return a 512-entry permutation table derived from ``seed``.

    The 256 values ``0..255`` are shuffled deterministically and the result is
    duplicated so that ``table[i] + offset`` never overflows the table bounds.
    """
    values = list(range(256))
    rng = xorshift32(seed)
    for i in range(255, 0, -1):
        j = rng() % (i + 1)
        values[i], values[j] = values[j], values[i]
    return tuple(values + values)
