"""Abstract base for noise generators.

Mirrors the TypeScript ``NoiseGenerator`` abstract class: it holds the seed that
selects the noise field. Concrete algorithms (e.g. Perlin) subclass it and
implement a dimension-specific ``noise(...)`` method.
"""

from abc import ABC


class NoiseGenerator(ABC):  # noqa: B024 - concept anchor; `noise` is dimension-specific (see interfaces)
    """Holds the seed shared by every dimension of a noise algorithm.

    Args:
        seed: Seed for the noise field; the same seed yields the same field.
    """

    def __init__(self, *, seed: int = 0) -> None:
        self._seed = seed
