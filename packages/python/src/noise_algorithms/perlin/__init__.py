"""Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

For each dimension, the following public entry points are provided:

- ``PerlinNoise{1,2,3}D`` — single-octave class (reuse for repeated sampling).
- ``perlin_{1,2,3}d`` — single-octave one-shot function (a value).
- ``perlin_line`` / ``perlin_grid`` / ``perlin_volume`` — single-octave one-shot
  over a whole region (a curve / image / volume).
- ``FractalPerlinNoise{1,2,3}D`` — fractal (multi-octave) class, stacking
  octaves of a Perlin source (extends
  :class:`~noise_algorithms.FractalNoiseGenerator`).
- ``fractal_perlin_{1,2,3}d`` — fractal one-shot function (a value).
- ``fractal_perlin_line`` / ``fractal_perlin_grid`` / ``fractal_perlin_volume``
  — fractal one-shot over a whole region.

Every generator returns noise in the ``[-1, 1]`` interval.
"""

from ._base import PerlinNoise
from .perlin_1d import (
    FractalPerlinNoise1D,
    PerlinNoise1D,
    fractal_perlin_1d,
    fractal_perlin_line,
    perlin_1d,
    perlin_line,
)
from .perlin_2d import (
    FractalPerlinNoise2D,
    PerlinNoise2D,
    fractal_perlin_2d,
    fractal_perlin_grid,
    perlin_2d,
    perlin_grid,
)
from .perlin_3d import (
    FractalPerlinNoise3D,
    PerlinNoise3D,
    fractal_perlin_3d,
    fractal_perlin_volume,
    perlin_3d,
    perlin_volume,
)

__all__ = [
    "PerlinNoise",
    "PerlinNoise1D",
    "PerlinNoise2D",
    "PerlinNoise3D",
    "perlin_1d",
    "perlin_2d",
    "perlin_3d",
    "perlin_line",
    "perlin_grid",
    "perlin_volume",
    "FractalPerlinNoise1D",
    "FractalPerlinNoise2D",
    "FractalPerlinNoise3D",
    "fractal_perlin_1d",
    "fractal_perlin_2d",
    "fractal_perlin_3d",
    "fractal_perlin_line",
    "fractal_perlin_grid",
    "fractal_perlin_volume",
]
