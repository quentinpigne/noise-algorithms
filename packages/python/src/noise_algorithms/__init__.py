"""A collection of noise generation algorithms in pure Python."""

from __future__ import annotations

from .perlin import PerlinConfig, perlin_1d, perlin_2d, perlin_3d

__all__ = ["PerlinConfig", "perlin_1d", "perlin_2d", "perlin_3d"]
__version__ = "0.1.0"
