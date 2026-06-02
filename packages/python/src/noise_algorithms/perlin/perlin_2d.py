"""2D Perlin noise."""

from __future__ import annotations

import math

from .._interpolation import fade, lerp
from ._config import DEFAULT_CONFIG, PerlinConfig
from ._fractal import fractal

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


def _octave(x: float, y: float, perm: tuple[int, ...]) -> float:
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


def perlin_2d(x: float, y: float, config: PerlinConfig = DEFAULT_CONFIG) -> float:
    """Return fractal 2D Perlin noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
    return fractal(_octave, (x, y), config)
