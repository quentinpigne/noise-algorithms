"""Seeded permutation table used to hash grid coordinates.

The table is built with the standard library's :class:`random.Random`
(a deterministic, version-stable Mersenne Twister) so the package keeps a
pure-Python, dependency-free runtime. Tables are cached per seed because they
are immutable and reused across every ``noise`` call sharing that seed.
"""

from __future__ import annotations

import random
from functools import cache


@cache
def permutation_table(seed: int) -> tuple[int, ...]:
    """Return a 512-entry permutation table derived from ``seed``.

    The 256 values ``0..255`` are shuffled deterministically and the result is
    duplicated so that ``table[i] + offset`` never overflows the table bounds.
    """
    values = list(range(256))
    random.Random(seed).shuffle(values)
    return tuple(values + values)
