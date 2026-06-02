"""3D Perlin noise."""

from __future__ import annotations

import math

from .._interpolation import fade, lerp
from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# 12 edge-midpoint directions of a cube, indexed with ``h % 12``.
_GRADIENTS = (
    (_UNIT, _UNIT, 0.0),
    (_UNIT, -_UNIT, 0.0),
    (-_UNIT, _UNIT, 0.0),
    (-_UNIT, -_UNIT, 0.0),
    (_UNIT, 0.0, _UNIT),
    (_UNIT, 0.0, -_UNIT),
    (-_UNIT, 0.0, _UNIT),
    (-_UNIT, 0.0, -_UNIT),
    (0.0, _UNIT, _UNIT),
    (0.0, _UNIT, -_UNIT),
    (0.0, -_UNIT, _UNIT),
    (0.0, -_UNIT, -_UNIT),
)


def _grad(h: int, x: float, y: float, z: float) -> float:
    gx, gy, gz = _GRADIENTS[h % 12]
    return x * gx + y * gy + z * gz


class PerlinNoise3D(PerlinNoise):
    """3D Perlin noise generator."""

    def noise(self, x: float, y: float, z: float) -> float:
        """Return fractal 3D Perlin noise at ``(x, y, z)`` in ``[-1, 1]``."""
        return self._fractal(x, y, z)

    def _octave(self, x: float, y: float, z: float) -> float:
        perm = self._perm
        x0 = math.floor(x) & 255
        x1 = (x0 + 1) & 255
        y0 = math.floor(y) & 255
        y1 = (y0 + 1) & 255
        z0 = math.floor(z) & 255
        z1 = (z0 + 1) & 255

        xf = x - math.floor(x)
        yf = y - math.floor(y)
        zf = z - math.floor(z)
        u = fade(xf)
        v = fade(yf)
        w = fade(zf)

        a = perm[x0]
        b = perm[x1]
        aa = perm[a + y0]
        ab = perm[a + y1]
        ba = perm[b + y0]
        bb = perm[b + y1]

        h000 = perm[perm[aa + z0]]
        h001 = perm[perm[aa + z1]]
        h010 = perm[perm[ab + z0]]
        h011 = perm[perm[ab + z1]]
        h100 = perm[perm[ba + z0]]
        h101 = perm[perm[ba + z1]]
        h110 = perm[perm[bb + z0]]
        h111 = perm[perm[bb + z1]]

        n000 = _grad(h000, xf, yf, zf)
        n001 = _grad(h001, xf, yf, zf - 1)
        n010 = _grad(h010, xf, yf - 1, zf)
        n011 = _grad(h011, xf, yf - 1, zf - 1)
        n100 = _grad(h100, xf - 1, yf, zf)
        n101 = _grad(h101, xf - 1, yf, zf - 1)
        n110 = _grad(h110, xf - 1, yf - 1, zf)
        n111 = _grad(h111, xf - 1, yf - 1, zf - 1)

        n00 = lerp(n000, n100, u)
        n01 = lerp(n001, n101, u)
        n10 = lerp(n010, n110, u)
        n11 = lerp(n011, n111, u)

        n0 = lerp(n00, n10, v)
        n1 = lerp(n01, n11, v)
        return lerp(n0, n1, w)


def perlin_3d(
    x: float,
    y: float,
    z: float,
    *,
    seed: int = 0,
    scale: float = 0.01,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """One-shot fractal 3D Perlin noise at ``(x, y, z)``.

    Convenience wrapper that builds a :class:`PerlinNoise3D` per call. For
    repeated sampling (e.g. rendering an image), instantiate
    :class:`PerlinNoise3D` once and reuse it.
    """
    generator = PerlinNoise3D(
        seed=seed,
        scale=scale,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
    )
    return generator.noise(x, y, z)
