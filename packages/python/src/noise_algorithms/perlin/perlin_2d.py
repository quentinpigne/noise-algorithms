"""2D Perlin noise."""

import math

from ..fractal_noise_generator import FractalNoiseGenerator
from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# 8 gradient directions, indexed with ``h & 7``.
_GRADIENTS = (
    (_UNIT, _UNIT),
    (-_UNIT, _UNIT),
    (_UNIT, -_UNIT),
    (-_UNIT, -_UNIT),
    (0.0, 1.0),
    (0.0, -1.0),
    (1.0, 0.0),
    (-1.0, 0.0),
)


class PerlinNoise2D(PerlinNoise):
    """2D Perlin noise generator (single octave)."""

    def noise(self, x: float, y: float) -> float:
        """Return a single octave of 2D Perlin noise at ``(x, y)`` in ``[-1, 1]``."""
        return self._octave(x, y)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        gx, gy = _GRADIENTS[h & 7]
        return displacement[0] * gx + displacement[1] * gy


def perlin_2d(x: float, y: float, *, seed: int = 0) -> float:
    """One-shot single octave of 2D Perlin noise at ``(x, y)``.

    Builds a :class:`PerlinNoise2D` per call; reuse an instance for loops.
    """
    return PerlinNoise2D(seed=seed).noise(x, y)


class FractalPerlinNoise2D(FractalNoiseGenerator):
    """Fractal (multi-octave) 2D Perlin noise.

    Stacks octaves of a :class:`PerlinNoise2D` source.
    """

    def __init__(
        self,
        *,
        seed: int = 0,
        octaves: int = 4,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
        frequency: float = 0.01,
    ) -> None:
        super().__init__(
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
        )
        self._source = PerlinNoise2D(seed=seed)

    def _sample(self, *coords: float) -> float:
        return self._source.noise(*coords)

    def noise(self, x: float, y: float) -> float:
        """Return fractal 2D noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
        return self._fractal(x, y)


def fractal_perlin_2d(
    x: float,
    y: float,
    *,
    seed: int = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
) -> float:
    """One-shot fractal 2D Perlin noise at ``(x, y)`` in ``[-1, 1]``.

    Builds a :class:`FractalPerlinNoise2D` per call; reuse an instance for loops.
    """
    return FractalPerlinNoise2D(
        seed=seed,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        frequency=frequency,
    ).noise(x, y)
