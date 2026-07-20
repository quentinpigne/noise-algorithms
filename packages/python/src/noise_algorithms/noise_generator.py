"""Abstract base for noise generators.

Mirrors the TypeScript ``NoiseGenerator`` abstract class: it holds the seed that
selects the noise field. Concrete algorithms (e.g. Perlin) subclass it and
implement a dimension-specific ``noise(...)`` method.
"""

from abc import ABC

from ._seeded_random import fnv1a32


class NoiseGenerator(ABC):  # noqa: B024 - concept anchor; `noise` is dimension-specific (see interfaces)
    """Holds the seed shared by every dimension of a noise algorithm.

    Args:
        seed: Seed for the noise field; the same seed yields the same field. A
            string is hashed to an integer, so named seeds (e.g. ``"my-world"``)
            work too.
    """

    def __init__(self, *, seed: int | str = 0) -> None:
        self._seed = fnv1a32(seed) if isinstance(seed, str) else seed
