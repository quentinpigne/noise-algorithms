"""Shared abstract base for the Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

The base implements a dimension-agnostic engine: hashing folds the permutation
table over the coordinates, every corner of the surrounding hypercube
contributes a gradient dot product, and the contributions are combined by a
pairwise lerp reduction along each axis. Subclasses only provide their
dimension-specific gradient set via ``_gradient``.
"""

import math
from abc import ABC, abstractmethod

from .._interpolation import fade, lerp
from .._permutation import build_permutation


class PerlinNoise(ABC):
    """Holds the parameters and the seeded permutation table.

    The permutation table is built once here and reused for every ``noise``
    call, so a generator is cheap to sample repeatedly.

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

    def _octave(self, *coords: float) -> float:
        """Single octave of N-dimensional Perlin noise at the given coordinates."""
        perm = self._perm
        n = len(coords)

        floors = [math.floor(c) for c in coords]
        cells = [f & 255 for f in floors]
        fracs = [c - f for c, f in zip(coords, floors, strict=True)]
        faded = [fade(f) for f in fracs]

        # Noise contribution of every corner of the surrounding hypercube; the
        # corner index encodes its offsets (bit ``axis`` = offset along ``axis``).
        values = []
        for corner in range(1 << n):
            h = perm[(cells[0] + (corner & 1)) & 255]
            for axis in range(1, n):
                h = perm[h + ((cells[axis] + ((corner >> axis) & 1)) & 255)]
            h = perm[h]

            displacement = [fracs[axis] - ((corner >> axis) & 1) for axis in range(n)]
            values.append(self._gradient(h, displacement))

        # Pairwise lerp reduction along each axis: 2^n -> 2^(n-1) -> ... -> 1.
        for axis in range(n):
            values = [
                lerp(values[i], values[i + 1], faded[axis])
                for i in range(0, len(values), 2)
            ]

        return values[0]

    @abstractmethod
    def _gradient(self, h: int, displacement: list[float]) -> float:
        """Dot product of the hashed gradient with the corner displacement."""
