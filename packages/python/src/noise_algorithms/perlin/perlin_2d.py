"""2D Perlin noise."""

import math

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
    """2D Perlin noise generator."""

    def noise(self, x: float, y: float) -> float:
        """Return fractal 2D Perlin noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
        return self._fractal(x, y)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        gx, gy = _GRADIENTS[h & 7]
        return displacement[0] * gx + displacement[1] * gy


def perlin_2d(
    x: float,
    y: float,
    *,
    seed: int = 0,
    scale: float = 0.01,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """One-shot fractal 2D Perlin noise at ``(x, y)``.

    Convenience wrapper that builds a :class:`PerlinNoise2D` per call. For
    repeated sampling (e.g. rendering an image), instantiate
    :class:`PerlinNoise2D` once and reuse it.
    """
    generator = PerlinNoise2D(
        seed=seed,
        scale=scale,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
    )
    return generator.noise(x, y)
