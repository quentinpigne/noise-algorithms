"""The sources of a fractal generator's octaves.

Mirrors ``octave-sources.ts`` in the TypeScript package, draw for draw: the
order below is part of the cross-language invariant.
"""

from collections.abc import Callable
from typing import TypeVar

from ._seeded_random import xorshift32
from .noise_generator import resolve_seed

T = TypeVar("T")

#: A coordinate offset spans one period of the permutation lattice.
_OFFSET_RANGE = 256

#: ``2**32``: turns a uint32 draw into ``[0, 1)``, exactly.
_UINT32_RANGE = 4294967296

#: Offsets drawn per octave, whatever the dimension: x, y, then z.
OFFSET_AXES = 3


def octave_sources(
    seed: int | str,
    count: int,
    independent: bool,
    make: Callable[[int], T],
) -> tuple[list[T], list[float]]:
    """Build the source of each octave, and its offsets.

    Shared, every octave samples one source built from the seed — plain fBm —
    and the offsets are all zero.

    Independent, the seed drives an xorshift32 stream: for each octave in turn,
    one draw seeds its source, then three draws give its x, y and z offsets in
    ``[0, 256)``. Three offsets are drawn in every dimension, so a 2D generator
    reads the same stream as a 3D one and leaves z unused.
    """
    offsets = [0.0] * (count * OFFSET_AXES)
    if not independent:
        shared = make(resolve_seed(seed))
        return [shared] * count, offsets

    random = xorshift32(resolve_seed(seed))
    sources: list[T] = []
    for octave in range(count):
        sources.append(make(random()))
        for axis in range(OFFSET_AXES):
            offsets[octave * OFFSET_AXES + axis] = (
                random() / _UINT32_RANGE
            ) * _OFFSET_RANGE
    return sources, offsets
