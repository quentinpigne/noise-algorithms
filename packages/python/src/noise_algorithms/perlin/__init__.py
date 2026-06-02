"""Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

Two equivalent APIs are provided:

- Classes :class:`PerlinNoise1D`, :class:`PerlinNoise2D`, :class:`PerlinNoise3D`
  build their permutation table once and are the right choice for repeated
  sampling (e.g. rendering an image).
- Functions :func:`perlin_1d`, :func:`perlin_2d`, :func:`perlin_3d` are one-shot
  convenience wrappers around those classes.

Every generator returns fractal (multi-octave) noise in the ``[-1, 1]`` interval.
"""

from __future__ import annotations

from ._base import PerlinNoise
from .perlin_1d import PerlinNoise1D, perlin_1d
from .perlin_2d import PerlinNoise2D, perlin_2d
from .perlin_3d import PerlinNoise3D, perlin_3d

__all__ = [
    "PerlinNoise",
    "PerlinNoise1D",
    "PerlinNoise2D",
    "PerlinNoise3D",
    "perlin_1d",
    "perlin_2d",
    "perlin_3d",
]
