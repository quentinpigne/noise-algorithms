"""Perlin noise generators.

See https://en.wikipedia.org/wiki/Perlin_noise

The public API is functional: call :func:`perlin_1d`, :func:`perlin_2d` or
:func:`perlin_3d` with a coordinate and an optional :class:`PerlinConfig`. Each
function returns fractal (multi-octave) noise in the ``[-1, 1]`` interval.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ._interpolation import fade, lerp
from ._permutation import permutation_table

_UNIT = 1.0 / math.sqrt(2)

# Gradient vectors. 2D uses 8 directions (indexed with ``h & 7``), 3D uses the
# 12 edge-midpoint directions of a cube (indexed with ``h % 12``).
_GRADIENTS_2D = (
    (_UNIT, _UNIT),
    (-_UNIT, _UNIT),
    (_UNIT, -_UNIT),
    (-_UNIT, -_UNIT),
    (0.0, 1.0),
    (0.0, -1.0),
    (1.0, 0.0),
    (-1.0, 0.0),
)

_GRADIENTS_3D = (
    (_UNIT, _UNIT, 0.0),
    (_UNIT, -_UNIT, 0.0),
    (-_UNIT, _UNIT, 0.0),
    (-_UNIT, -_UNIT, 0.0),
    (_UNIT, 0.0, _UNIT),
    (_UNIT, 0.0, -_UNIT),
    (-_UNIT, 0.0, _UNIT),
    (-_UNIT, 0.0, -_UNIT),
    (0.0, _UNIT, _UNIT),
    (0.0, _UNIT, -_UNIT),
    (0.0, -_UNIT, _UNIT),
    (0.0, -_UNIT, -_UNIT),
)


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


_DEFAULT_CONFIG = PerlinConfig()


def _grad_2d(h: int, x: float, y: float) -> float:
    gx, gy = _GRADIENTS_2D[h & 7]
    return x * gx + y * gy


def _grad_3d(h: int, x: float, y: float, z: float) -> float:
    gx, gy, gz = _GRADIENTS_3D[h % 12]
    return x * gx + y * gy + z * gz


def _noise_1d(x: float, perm: tuple[int, ...]) -> float:
    x0 = math.floor(x) & 255
    x1 = (x0 + 1) & 255

    xf = x - math.floor(x)
    u = fade(xf)

    h0 = perm[perm[x0]]
    h1 = perm[perm[x1]]

    n0 = xf if (h0 & 1) == 0 else -xf
    n1 = (xf - 1) if (h1 & 1) == 0 else -(xf - 1)

    return lerp(n0, n1, u)


def _noise_2d(x: float, y: float, perm: tuple[int, ...]) -> float:
    x0 = math.floor(x) & 255
    x1 = (x0 + 1) & 255
    y0 = math.floor(y) & 255
    y1 = (y0 + 1) & 255

    xf = x - math.floor(x)
    yf = y - math.floor(y)
    u = fade(xf)
    v = fade(yf)

    a = perm[x0]
    b = perm[x1]
    h00 = perm[perm[a + y0]]
    h01 = perm[perm[a + y1]]
    h10 = perm[perm[b + y0]]
    h11 = perm[perm[b + y1]]

    n00 = _grad_2d(h00, xf, yf)
    n01 = _grad_2d(h01, xf, yf - 1)
    n10 = _grad_2d(h10, xf - 1, yf)
    n11 = _grad_2d(h11, xf - 1, yf - 1)

    n0 = lerp(n00, n10, u)
    n1 = lerp(n01, n11, u)
    return lerp(n0, n1, v)


def _noise_3d(x: float, y: float, z: float, perm: tuple[int, ...]) -> float:
    x0 = math.floor(x) & 255
    x1 = (x0 + 1) & 255
    y0 = math.floor(y) & 255
    y1 = (y0 + 1) & 255
    z0 = math.floor(z) & 255
    z1 = (z0 + 1) & 255

    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u = fade(xf)
    v = fade(yf)
    w = fade(zf)

    a = perm[x0]
    b = perm[x1]
    aa = perm[a + y0]
    ab = perm[a + y1]
    ba = perm[b + y0]
    bb = perm[b + y1]

    h000 = perm[perm[aa + z0]]
    h001 = perm[perm[aa + z1]]
    h010 = perm[perm[ab + z0]]
    h011 = perm[perm[ab + z1]]
    h100 = perm[perm[ba + z0]]
    h101 = perm[perm[ba + z1]]
    h110 = perm[perm[bb + z0]]
    h111 = perm[perm[bb + z1]]

    n000 = _grad_3d(h000, xf, yf, zf)
    n001 = _grad_3d(h001, xf, yf, zf - 1)
    n010 = _grad_3d(h010, xf, yf - 1, zf)
    n011 = _grad_3d(h011, xf, yf - 1, zf - 1)
    n100 = _grad_3d(h100, xf - 1, yf, zf)
    n101 = _grad_3d(h101, xf - 1, yf, zf - 1)
    n110 = _grad_3d(h110, xf - 1, yf - 1, zf)
    n111 = _grad_3d(h111, xf - 1, yf - 1, zf - 1)

    n00 = lerp(n000, n100, u)
    n01 = lerp(n001, n101, u)
    n10 = lerp(n010, n110, u)
    n11 = lerp(n011, n111, u)

    n0 = lerp(n00, n10, v)
    n1 = lerp(n01, n11, v)
    return lerp(n0, n1, w)


def perlin_1d(x: float, config: PerlinConfig = _DEFAULT_CONFIG) -> float:
    """Return fractal 1D Perlin noise at ``x`` in the ``[-1, 1]`` interval."""
    perm = permutation_table(config.seed)

    value = 0.0
    max_value = 0.0
    amplitude = 1.0
    frequency = 1.0

    for _ in range(config.octaves):
        value += _noise_1d(x * frequency * config.scale, perm) * amplitude
        max_value += amplitude
        amplitude *= config.persistence
        frequency *= config.lacunarity

    return value / max_value


def perlin_2d(x: float, y: float, config: PerlinConfig = _DEFAULT_CONFIG) -> float:
    """Return fractal 2D Perlin noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
    perm = permutation_table(config.seed)

    value = 0.0
    max_value = 0.0
    amplitude = 1.0
    frequency = 1.0

    for _ in range(config.octaves):
        value += (
            _noise_2d(
                x * frequency * config.scale,
                y * frequency * config.scale,
                perm,
            )
            * amplitude
        )
        max_value += amplitude
        amplitude *= config.persistence
        frequency *= config.lacunarity

    return value / max_value


def perlin_3d(
    x: float, y: float, z: float, config: PerlinConfig = _DEFAULT_CONFIG
) -> float:
    """Return fractal 3D Perlin noise at ``(x, y, z)`` in the ``[-1, 1]`` interval."""
    perm = permutation_table(config.seed)

    value = 0.0
    max_value = 0.0
    amplitude = 1.0
    frequency = 1.0

    for _ in range(config.octaves):
        value += (
            _noise_3d(
                x * frequency * config.scale,
                y * frequency * config.scale,
                z * frequency * config.scale,
                perm,
            )
            * amplitude
        )
        max_value += amplitude
        amplitude *= config.persistence
        frequency *= config.lacunarity

    return value / max_value
