"""A collection of noise generation algorithms in pure Python."""

from __future__ import annotations

from .interfaces import NoiseGenerator1D, NoiseGenerator2D, NoiseGenerator3D
from .perlin import (
    PerlinNoise,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
    perlin_1d,
    perlin_2d,
    perlin_3d,
)

__all__ = [
    "NoiseGenerator1D",
    "NoiseGenerator2D",
    "NoiseGenerator3D",
    "PerlinNoise",
    "PerlinNoise1D",
    "PerlinNoise2D",
    "PerlinNoise3D",
    "perlin_1d",
    "perlin_2d",
    "perlin_3d",
]
__version__ = "0.1.0"
