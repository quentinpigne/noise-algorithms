"""Configuration shared by the Perlin noise generators."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerlinConfig:
    """Parameters controlling fractal Perlin noise.

    Attributes:
        seed: Seed for the permutation table. The same seed always yields the
            same noise field.
        scale: Base frequency multiplier applied to the input coordinates.
        octaves: Number of noise layers summed together.
        lacunarity: Frequency multiplier between successive octaves.
        persistence: Amplitude multiplier between successive octaves.
    """

    seed: int = 0
    scale: float = 0.01
    octaves: int = 4
    lacunarity: float = 2.0
    persistence: float = 0.5


DEFAULT_CONFIG = PerlinConfig()
