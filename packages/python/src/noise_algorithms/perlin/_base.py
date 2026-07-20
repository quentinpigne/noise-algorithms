"""Shared abstract base for the Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

The base implements a dimension-agnostic engine: hashing folds the permutation
table over the coordinates, every corner of the surrounding hypercube
contributes a gradient dot product, and the contributions are combined by a
pairwise lerp reduction along each axis. Subclasses only provide their
dimension-specific gradient set via ``_gradient``.
"""

import math
from abc import abstractmethod

from .._interpolation import fade, lerp
from .._permutation import build_permutation
from ..noise_generator import NoiseGenerator


class PerlinNoise(NoiseGenerator):
    """Holds the seeded permutation table for a single octave of gradient noise.

    The permutation table is built once here and reused for every ``noise``
    call, so a generator is cheap to sample repeatedly. For multi-octave
    (fractal) noise, use :class:`~noise_algorithms.FractalPerlinNoise1D` (or
    2D/3D).

    Args:
        seed: Seed for the permutation table; the same seed yields the same field.
    """

    # Multiplier that scales a raw octave to the full [-1, 1] range (reciprocal
    # of the gradient set's maximum magnitude). Set by each dimension subclass.
    _NORMALIZATION: float

    def __init__(self, *, seed: int | str = 0) -> None:
        super().__init__(seed=seed)
        self._permutation = build_permutation(self._seed)

    def _octave(self, *coords: float) -> float:
        """Single octave of N-dimensional Perlin noise at the given coordinates."""
        permutation = self._permutation
        n = len(coords)

        floors = [math.floor(c) for c in coords]
        cells = [f & 255 for f in floors]
        fracs = [c - f for c, f in zip(coords, floors, strict=True)]
        faded = [fade(f) for f in fracs]

        # Noise contribution of every corner of the surrounding hypercube; the
        # corner index encodes its offsets (bit ``axis`` = offset along ``axis``).
        values = []
        for corner in range(1 << n):
            h = permutation[(cells[0] + (corner & 1)) & 255]
            for axis in range(1, n):
                h = permutation[h + ((cells[axis] + ((corner >> axis) & 1)) & 255)]
            h = permutation[h]

            displacement = [fracs[axis] - ((corner >> axis) & 1) for axis in range(n)]
            values.append(self._gradient(h, displacement))

        # Pairwise lerp reduction along each axis: 2^n -> 2^(n-1) -> ... -> 1.
        for axis in range(n):
            values = [
                lerp(values[i], values[i + 1], faded[axis])
                for i in range(0, len(values), 2)
            ]

        # Raw gradient noise under-fills [-1, 1]; scale it to the full range, then
        # clamp to honour the documented contract.
        value = values[0] * self._NORMALIZATION
        return max(-1.0, min(1.0, value))

    @abstractmethod
    def _gradient(self, h: int, displacement: list[float]) -> float:
        """Dot product of the hashed gradient with the corner displacement."""
