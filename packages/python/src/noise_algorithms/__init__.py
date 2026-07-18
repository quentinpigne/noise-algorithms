"""A collection of noise generation algorithms in pure Python."""

from .fractal_noise_generator import FractalNoiseGenerator
from .interfaces import (
    FractalNoiseGenerator1D,
    FractalNoiseGenerator2D,
    FractalNoiseGenerator3D,
    NoiseGenerator1D,
    NoiseGenerator2D,
    NoiseGenerator3D,
)
from .noise_generator import NoiseGenerator
from .perlin import (
    FractalPerlinNoise1D,
    FractalPerlinNoise2D,
    FractalPerlinNoise3D,
    PerlinNoise,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
    fractal_perlin_1d,
    fractal_perlin_2d,
    fractal_perlin_3d,
    perlin_1d,
    perlin_2d,
    perlin_3d,
)

__all__ = [
    # Abstract concepts
    "NoiseGenerator",
    "FractalNoiseGenerator",
    # Dimension interfaces (protocols)
    "NoiseGenerator1D",
    "NoiseGenerator2D",
    "NoiseGenerator3D",
    "FractalNoiseGenerator1D",
    "FractalNoiseGenerator2D",
    "FractalNoiseGenerator3D",
    # Perlin — single octave
    "PerlinNoise",
    "PerlinNoise1D",
    "PerlinNoise2D",
    "PerlinNoise3D",
    "perlin_1d",
    "perlin_2d",
    "perlin_3d",
    # Perlin — fractal
    "FractalPerlinNoise1D",
    "FractalPerlinNoise2D",
    "FractalPerlinNoise3D",
    "fractal_perlin_1d",
    "fractal_perlin_2d",
    "fractal_perlin_3d",
]
__version__ = "0.1.0"
