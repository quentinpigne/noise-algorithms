"""Shared abstract base for the Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .._permutation import build_permutation


class PerlinNoise(ABC):
    """Holds the parameters and the seeded permutation table.

    The permutation table is built once here and reused for every ``noise``
    call, so a generator is cheap to sample repeatedly. Subclasses implement
    ``_octave`` for their dimension; ``_fractal`` sums the octaves.

    Args:
        seed: Seed for the permutation table; the same seed yields the same field.
        scale: Base frequency multiplier applied to the input coordinates.
        octaves: Number of noise layers summed together.
        lacunarity: Frequency multiplier between successive octaves.
        persistence: Amplitude multiplier between successive octaves.
    """

    def __init__(
        self,
        seed: int = 0,
        scale: float = 0.01,
        octaves: int = 4,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
    ) -> None:
        self._perm = build_permutation(seed)
        self._scale = scale
        self._octaves = octaves
        self._lacunarity = lacunarity
        self._persistence = persistence

    def _fractal(self, *coords: float) -> float:
        """Sum ``octaves`` layers of ``_octave``; result is in ``[-1, 1]``."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = 1.0

        for _ in range(self._octaves):
            scaled = tuple(c * frequency * self._scale for c in coords)
            value += self._octave(*scaled) * amplitude
            max_value += amplitude
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value

    @abstractmethod
    def _octave(self, *coords: float) -> float:
        """Return one octave of noise at the given (already scaled) coordinates."""
