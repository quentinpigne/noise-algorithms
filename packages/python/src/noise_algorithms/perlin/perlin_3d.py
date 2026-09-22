"""3D Perlin noise."""

import math

from .._interpolation import fade, lerp
from ..fractal_noise_generator import FractalNoiseGenerator
from ..sampling import sample_volume
from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# Ken Perlin's improved-noise gradient set: the 12 cube-edge midpoints plus 4
# balanced duplicates (indices 12-15), so a power-of-2 mask ``h & 15`` selects
# uniformly with no modulo bias.
_VECTORS = (
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

#: The same table, flattened: ``_GRADIENTS[(h & 15) * 3 + axis]``.
_GRADIENTS = tuple(component for vector in _VECTORS for component in vector)


def _gradient(h: int, x: float, y: float, z: float) -> float:
    """Dot product of the hashed gradient with the corner displacement."""
    i = (h & 15) * 3
    return x * _GRADIENTS[i] + y * _GRADIENTS[i + 1] + z * _GRADIENTS[i + 2]


class PerlinNoise3D(PerlinNoise):
    """3D Perlin noise generator (single octave)."""

    # The gradients each have a zero component, so 3D noise peaks at ±√2/2
    # (not ±√3/2); ×√2 fills [-1, 1].
    _NORMALIZATION = math.sqrt(2)

    def noise(self, x: float, y: float, z: float) -> float:
        """Return a single octave of 3D Perlin noise at ``(x, y, z)`` in ``[-1, 1]``."""
        p = self._permutation

        floor_x = math.floor(x)
        floor_y = math.floor(y)
        floor_z = math.floor(z)

        # Displacements from the low corner, and from the high one a unit away.
        low_x = x - floor_x
        low_y = y - floor_y
        low_z = z - floor_z
        high_x = low_x - 1
        high_y = low_y - 1
        high_z = low_z - 1

        u = fade(low_x)
        v = fade(low_y)
        w = fade(low_z)

        x0 = floor_x & 255
        y0 = floor_y & 255
        z0 = floor_z & 255
        x1 = (x0 + 1) & 255
        y1 = (y0 + 1) & 255
        z1 = (z0 + 1) & 255

        # The permutation folds one axis at a time, so the prefixes are shared:
        # eight corners cost twelve lookups here instead of thirty-two.
        px0 = p[x0]
        px1 = p[x1]
        px0y0 = p[px0 + y0]
        px0y1 = p[px0 + y1]
        px1y0 = p[px1 + y0]
        px1y1 = p[px1 + y1]

        # Interpolate along x, then y, then z — the reduction order the generic
        # engine used, kept so the arithmetic is identical.
        xy00 = lerp(
            _gradient(p[p[px0y0 + z0]], low_x, low_y, low_z),
            _gradient(p[p[px1y0 + z0]], high_x, low_y, low_z),
            u,
        )
        xy10 = lerp(
            _gradient(p[p[px0y1 + z0]], low_x, high_y, low_z),
            _gradient(p[p[px1y1 + z0]], high_x, high_y, low_z),
            u,
        )
        xy01 = lerp(
            _gradient(p[p[px0y0 + z1]], low_x, low_y, high_z),
            _gradient(p[p[px1y0 + z1]], high_x, low_y, high_z),
            u,
        )
        xy11 = lerp(
            _gradient(p[p[px0y1 + z1]], low_x, high_y, high_z),
            _gradient(p[p[px1y1 + z1]], high_x, high_y, high_z),
            u,
        )

        return self._scaled(lerp(lerp(xy00, xy10, v), lerp(xy01, xy11, v), w))

    def _gradient(self, h: int, displacement: list[float]) -> float:
        # Feeds the generic ``_octave`` only — see :class:`PerlinNoise`.
        gx, gy, gz = _VECTORS[h & 15]
        return displacement[0] * gx + displacement[1] * gy + displacement[2] * gz


def perlin_3d(x: float, y: float, z: float, *, seed: int | str = 0) -> float:
    """One-shot single octave of 3D Perlin noise at ``(x, y, z)``.

    Builds a :class:`PerlinNoise3D` per call; reuse an instance for loops.
    """
    return PerlinNoise3D(seed=seed).noise(x, y, z)


def perlin_volume(
    *,
    width: int,
    height: int,
    depth: int,
    seed: int | str = 0,
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
        seed: int | str = 0,
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
        # Feeds the generic ``_fractal`` only — see :class:`FractalNoiseGenerator`.
        return self._source.noise(*coords)

    def noise(self, x: float, y: float, z: float) -> float:
        """Return fractal 3D noise at ``(x, y, z)`` in the ``[-1, 1]`` interval."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = self._frequency
        source = self._source.noise

        for _ in range(self._octaves):
            value += source(x * frequency, y * frequency, z * frequency) * amplitude
            max_value += amplitude
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value


def fractal_perlin_3d(
    x: float,
    y: float,
    z: float,
    *,
    seed: int | str = 0,
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
    seed: int | str = 0,
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
