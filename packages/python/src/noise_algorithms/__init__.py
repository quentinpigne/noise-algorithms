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
from .output_range import to_unit_range
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
    fractal_perlin_grid,
    fractal_perlin_line,
    fractal_perlin_volume,
    perlin_1d,
    perlin_2d,
    perlin_3d,
    perlin_grid,
    perlin_line,
    perlin_volume,
)
from .sampling import sample_grid, sample_line, sample_volume

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
    "perlin_line",
    "perlin_grid",
    "perlin_volume",
    # Perlin — fractal
    "FractalPerlinNoise1D",
    "FractalPerlinNoise2D",
    "FractalPerlinNoise3D",
    "fractal_perlin_1d",
    "fractal_perlin_2d",
    "fractal_perlin_3d",
    "fractal_perlin_line",
    "fractal_perlin_grid",
    "fractal_perlin_volume",
    # Generic region sampling (curve / image / volume)
    "sample_line",
    "sample_grid",
    "sample_volume",
    # Output range
    "to_unit_range",
]
__version__ = "1.0.0"
