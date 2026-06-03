"""2D Perlin noise."""

import math

from .._interpolation import fade, lerp
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


def _grad(h: int, x: float, y: float) -> float:
    gx, gy = _GRADIENTS[h & 7]
    return x * gx + y * gy


class PerlinNoise2D(PerlinNoise):
    """2D Perlin noise generator."""

    def noise(self, x: float, y: float) -> float:
        """Return fractal 2D Perlin noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
        return self._fractal(x, y)

    def _octave(self, x: float, y: float) -> float:
        perm = self._perm
        x0 = math.floor(x) & 255
        x1 = (x0 + 1) & 255
        y0 = math.floor(y) & 255
        y1 = (y0 + 1) & 255

        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = fade(xf)
        v = fade(yf)

        a = perm[x0]
        b = perm[x1]
        h00 = perm[perm[a + y0]]
        h01 = perm[perm[a + y1]]
        h10 = perm[perm[b + y0]]
        h11 = perm[perm[b + y1]]

        n00 = _grad(h00, xf, yf)
        n01 = _grad(h01, xf, yf - 1)
        n10 = _grad(h10, xf - 1, yf)
        n11 = _grad(h11, xf - 1, yf - 1)

        n0 = lerp(n00, n10, u)
        n1 = lerp(n01, n11, u)
        return lerp(n0, n1, v)


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
