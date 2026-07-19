"""3D Perlin noise."""

import math

from ..fractal_noise_generator import FractalNoiseGenerator
from ..sampling import sample_volume
from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# Ken Perlin's improved-noise gradient set: the 12 cube-edge midpoints plus 4
# balanced duplicates (indices 12-15), so a power-of-2 mask ``h & 15`` selects
# uniformly with no modulo bias.
_GRADIENTS = (
    (_UNIT, _UNIT, 0.0),
    (-_UNIT, _UNIT, 0.0),
    (_UNIT, -_UNIT, 0.0),
    (-_UNIT, -_UNIT, 0.0),
    (_UNIT, 0.0, _UNIT),
    (-_UNIT, 0.0, _UNIT),
    (_UNIT, 0.0, -_UNIT),
    (-_UNIT, 0.0, -_UNIT),
    (0.0, _UNIT, _UNIT),
    (0.0, -_UNIT, _UNIT),
    (0.0, _UNIT, -_UNIT),
    (0.0, -_UNIT, -_UNIT),
    (_UNIT, _UNIT, 0.0),
    (0.0, -_UNIT, _UNIT),
    (-_UNIT, _UNIT, 0.0),
    (0.0, -_UNIT, -_UNIT),
)


class PerlinNoise3D(PerlinNoise):
    """3D Perlin noise generator (single octave)."""

    # The gradients each have a zero component, so 3D noise peaks at ±√2/2
    # (not ±√3/2); ×√2 fills [-1, 1].
    _NORMALIZATION = math.sqrt(2)

    def noise(self, x: float, y: float, z: float) -> float:
        """Return a single octave of 3D Perlin noise at ``(x, y, z)`` in ``[-1, 1]``."""
        return self._octave(x, y, z)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        gx, gy, gz = _GRADIENTS[h & 15]
        return displacement[0] * gx + displacement[1] * gy + displacement[2] * gz


def perlin_3d(x: float, y: float, z: float, *, seed: int = 0) -> float:
    """One-shot single octave of 3D Perlin noise at ``(x, y, z)``.

    Builds a :class:`PerlinNoise3D` per call; reuse an instance for loops.
    """
    return PerlinNoise3D(seed=seed).noise(x, y, z)


def perlin_volume(
    *,
    width: int,
    height: int,
    depth: int,
    seed: int = 0,
    start_x: float = 0.0,
    start_y: float = 0.0,
    start_z: float = 0.0,
    step: float = 1.0,
) -> list[list[list[float]]]:
    """One-shot single octave of 3D Perlin noise over a regular volume.

    Builds a :class:`PerlinNoise3D` and samples it with
    :func:`~noise_algorithms.sample_volume`.
    """
    return sample_volume(
        PerlinNoise3D(seed=seed),
        width=width,
        height=height,
        depth=depth,
        start_x=start_x,
        start_y=start_y,
        start_z=start_z,
        step=step,
    )


class FractalPerlinNoise3D(FractalNoiseGenerator):
    """Fractal (multi-octave) 3D Perlin noise.

    Stacks octaves of a :class:`PerlinNoise3D` source.
    """

    def __init__(
        self,
        *,
        seed: int = 0,
        octaves: int = 4,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
        frequency: float = 0.01,
    ) -> None:
        super().__init__(
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
        )
        self._source = PerlinNoise3D(seed=seed)

    def _sample(self, *coords: float) -> float:
        return self._source.noise(*coords)

    def noise(self, x: float, y: float, z: float) -> float:
        """Return fractal 3D noise at ``(x, y, z)`` in the ``[-1, 1]`` interval."""
        return self._fractal(x, y, z)


def fractal_perlin_3d(
    x: float,
    y: float,
    z: float,
    *,
    seed: int = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
) -> float:
    """One-shot fractal 3D Perlin noise at ``(x, y, z)`` in ``[-1, 1]``.

    Builds a :class:`FractalPerlinNoise3D` per call; reuse an instance for loops.
    """
    return FractalPerlinNoise3D(
        seed=seed,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        frequency=frequency,
    ).noise(x, y, z)


def fractal_perlin_volume(
    *,
    width: int,
    height: int,
    depth: int,
    seed: int = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    start_x: float = 0.0,
    start_y: float = 0.0,
    start_z: float = 0.0,
    step: float = 1.0,
) -> list[list[list[float]]]:
    """One-shot fractal 3D Perlin noise over a regular volume.

    Builds a :class:`FractalPerlinNoise3D` and samples it with
    :func:`~noise_algorithms.sample_volume`.
    """
    return sample_volume(
        FractalPerlinNoise3D(
            seed=seed,
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
        ),
        width=width,
        height=height,
        depth=depth,
        start_x=start_x,
        start_y=start_y,
        start_z=start_z,
        step=step,
    )
