"""Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

The API is functional: call :func:`perlin_1d`, :func:`perlin_2d` or
:func:`perlin_3d` with a coordinate and an optional :class:`PerlinConfig`. Each
function returns fractal (multi-octave) noise in the ``[-1, 1]`` interval.
"""

from __future__ import annotations

from ._config import PerlinConfig
from .perlin_1d import perlin_1d
from .perlin_2d import perlin_2d
from .perlin_3d import perlin_3d

__all__ = ["PerlinConfig", "perlin_1d", "perlin_2d", "perlin_3d"]
