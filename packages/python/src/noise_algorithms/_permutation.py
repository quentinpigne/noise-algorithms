"""Seeded permutation table used to hash grid coordinates.

The table is built with the standard library's :class:`random.Random`
(a deterministic, version-stable Mersenne Twister) so the package keeps a
pure-Python, dependency-free runtime. Each noise generator builds its table once
in its constructor and holds it for its lifetime.
"""

from __future__ import annotations

import random


def build_permutation(seed: int) -> tuple[int, ...]:
    """Return a 512-entry permutation table derived from ``seed``.

    The 256 values ``0..255`` are shuffled deterministically and the result is
    duplicated so that ``table[i] + offset`` never overflows the table bounds.
    """
    values = list(range(256))
    random.Random(seed).shuffle(values)
    return tuple(values + values)
