"""3D Perlin noise."""

import math

from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# 12 edge-midpoint directions of a cube, indexed with ``h % 12``.
_GRADIENTS = (
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


class PerlinNoise3D(PerlinNoise):
    """3D Perlin noise generator."""

    def noise(self, x: float, y: float, z: float) -> float:
        """Return fractal 3D Perlin noise at ``(x, y, z)`` in ``[-1, 1]``."""
        return self._fractal(x, y, z)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        gx, gy, gz = _GRADIENTS[h % 12]
        return displacement[0] * gx + displacement[1] * gy + displacement[2] * gz


def perlin_3d(
    x: float,
    y: float,
    z: float,
    *,
    seed: int = 0,
    scale: float = 0.01,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """One-shot fractal 3D Perlin noise at ``(x, y, z)``.

    Convenience wrapper that builds a :class:`PerlinNoise3D` per call. For
    repeated sampling (e.g. rendering an image), instantiate
    :class:`PerlinNoise3D` once and reuse it.
    """
    generator = PerlinNoise3D(
        seed=seed,
        scale=scale,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
    )
    return generator.noise(x, y, z)
