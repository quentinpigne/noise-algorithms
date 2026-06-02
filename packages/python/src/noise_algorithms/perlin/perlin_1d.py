"""1D Perlin noise."""

from __future__ import annotations

import math

from .._interpolation import fade, lerp
from ._config import DEFAULT_CONFIG, PerlinConfig
from ._fractal import fractal


def _octave(x: float, perm: tuple[int, ...]) -> float:
    x0 = math.floor(x) & 255
    x1 = (x0 + 1) & 255

    xf = x - math.floor(x)
    u = fade(xf)

    h0 = perm[perm[x0]]
    h1 = perm[perm[x1]]

    n0 = xf if (h0 & 1) == 0 else -xf
    n1 = (xf - 1) if (h1 & 1) == 0 else -(xf - 1)

    return lerp(n0, n1, u)


def perlin_1d(x: float, config: PerlinConfig = DEFAULT_CONFIG) -> float:
    """Return fractal 1D Perlin noise at ``x`` in the ``[-1, 1]`` interval."""
    return fractal(_octave, (x,), config)
