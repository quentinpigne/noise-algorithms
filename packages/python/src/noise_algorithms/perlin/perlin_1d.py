"""1D Perlin noise."""

from __future__ import annotations

import math

from .._interpolation import fade, lerp
from ._base import PerlinNoise


class PerlinNoise1D(PerlinNoise):
    """1D Perlin noise generator."""

    def noise(self, x: float) -> float:
        """Return fractal 1D Perlin noise at ``x`` in the ``[-1, 1]`` interval."""
        return self._fractal(x)

    def _octave(self, x: float) -> float:
        perm = self._perm
        x0 = math.floor(x) & 255
        x1 = (x0 + 1) & 255

        xf = x - math.floor(x)
        u = fade(xf)

        h0 = perm[perm[x0]]
        h1 = perm[perm[x1]]

        n0 = xf if (h0 & 1) == 0 else -xf
        n1 = (xf - 1) if (h1 & 1) == 0 else -(xf - 1)

        return lerp(n0, n1, u)


def perlin_1d(
    x: float,
    *,
    seed: int = 0,
    scale: float = 0.01,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """One-shot fractal 1D Perlin noise at ``x``.

    Convenience wrapper that builds a :class:`PerlinNoise1D` per call. For
    repeated sampling (e.g. rendering an image), instantiate
    :class:`PerlinNoise1D` once and reuse it.
    """
    generator = PerlinNoise1D(
        seed=seed,
        scale=scale,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
    )
    return generator.noise(x)
