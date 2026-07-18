"""Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

For each dimension, four public entry points are provided:

- ``PerlinNoise{1,2,3}D`` — single-octave class (reuse for repeated sampling).
- ``perlin_{1,2,3}d`` — single-octave one-shot function.
- ``FractalPerlinNoise{1,2,3}D`` — fractal (multi-octave) class, stacking
  octaves of a Perlin source (extends
  :class:`~noise_algorithms.FractalNoiseGenerator`).
- ``fractal_perlin_{1,2,3}d`` — fractal one-shot function.

Every generator returns noise in the ``[-1, 1]`` interval.
"""

from ._base import PerlinNoise
from .perlin_1d import FractalPerlinNoise1D, PerlinNoise1D, fractal_perlin_1d, perlin_1d
from .perlin_2d import FractalPerlinNoise2D, PerlinNoise2D, fractal_perlin_2d, perlin_2d
from .perlin_3d import FractalPerlinNoise3D, PerlinNoise3D, fractal_perlin_3d, perlin_3d

__all__ = [
    "PerlinNoise",
    "PerlinNoise1D",
    "PerlinNoise2D",
    "PerlinNoise3D",
    "perlin_1d",
    "perlin_2d",
    "perlin_3d",
    "FractalPerlinNoise1D",
    "FractalPerlinNoise2D",
    "FractalPerlinNoise3D",
    "fractal_perlin_1d",
    "fractal_perlin_2d",
    "fractal_perlin_3d",
]
