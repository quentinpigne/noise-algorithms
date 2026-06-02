"""Fractal (multi-octave) summation shared by every Perlin dimension."""

from __future__ import annotations

from collections.abc import Callable

from .._permutation import permutation_table
from ._config import PerlinConfig


def fractal(
    octave: Callable[..., float],
    coords: tuple[float, ...],
    config: PerlinConfig,
) -> float:
    """Sum ``config.octaves`` layers of a single-octave noise function.

    ``octave`` is called with the scaled coordinates followed by the permutation
    table and must return one octave of noise in ``[-1, 1]``. The result is
    normalised back into ``[-1, 1]``.
    """
    perm = permutation_table(config.seed)

    value = 0.0
    max_value = 0.0
    amplitude = 1.0
    frequency = 1.0

    for _ in range(config.octaves):
        scaled = tuple(c * frequency * config.scale for c in coords)
        value += octave(*scaled, perm) * amplitude
        max_value += amplitude
        amplitude *= config.persistence
        frequency *= config.lacunarity

    return value / max_value
