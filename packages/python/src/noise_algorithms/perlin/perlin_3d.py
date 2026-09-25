"""3D Perlin noise."""

import math
from collections.abc import Sequence

from .._interpolation import fade, lerp
from .._octave_sources import OFFSET_AXES, octave_sources
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
        octaves: int | None = None,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
        frequency: float = 0.01,
        amplitudes: Sequence[float] | None = None,
        independent_octaves: bool = False,
    ) -> None:
        super().__init__(
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
            amplitudes=amplitudes,
            independent_octaves=independent_octaves,
        )
        self._sources, self._offsets = octave_sources(
            seed, self._octaves, independent_octaves, lambda s: PerlinNoise3D(seed=s)
        )

    def _sample(self, *coords: float, octave: int = 0) -> float:
        # Feeds the generic ``_fractal`` only — see :class:`FractalNoiseGenerator`.
        source = self._sources[octave]
        if not self._independent_octaves:
            return source.noise(*coords)
        at = octave * OFFSET_AXES
        return source.noise(
            coords[0] + self._offsets[at + 0],
            coords[1] + self._offsets[at + 1],
            coords[2] + self._offsets[at + 2],
        )

    def noise(self, x: float, y: float, z: float) -> float:
        """Return fractal 3D noise at ``(x, y, z)`` in the ``[-1, 1]`` interval."""
        if self._independent_octaves:
            return self._independent_noise(x, y, z)

        # Plain fBm, inlined: one source, sampled at every frequency.
        value = 0.0
        source = self._sources[0].noise
        frequencies = self._octave_frequencies
        amplitudes = self._octave_amplitudes
        weights = self._weights

        for octave in range(self._octaves):
            weight = weights[octave]
            if weight != 0:
                frequency = frequencies[octave]
                value += (
                    source(x * frequency, y * frequency, z * frequency)
                    * amplitudes[octave]
                    * weight
                )

        return value / self._amplitude_sum

    def _independent_noise(self, x: float, y: float, z: float) -> float:
        """Each octave samples its own source, from its own offset."""
        value = 0.0
        sources = self._sources
        offsets = self._offsets
        frequencies = self._octave_frequencies
        amplitudes = self._octave_amplitudes
        weights = self._weights

        for octave in range(self._octaves):
            weight = weights[octave]
            if weight != 0:
                frequency = frequencies[octave]
                at = octave * OFFSET_AXES
                value += (
                    sources[octave].noise(
                        x * frequency + offsets[at + 0],
                        y * frequency + offsets[at + 1],
                        z * frequency + offsets[at + 2],
                    )
                    * amplitudes[octave]
                    * weight
                )

        return value / self._amplitude_sum


def fractal_perlin_3d(
    x: float,
    y: float,
    z: float,
    *,
    seed: int | str = 0,
    octaves: int | None = None,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    amplitudes: Sequence[float] | None = None,
    independent_octaves: bool = False,
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
        amplitudes=amplitudes,
        independent_octaves=independent_octaves,
    ).noise(x, y, z)


def fractal_perlin_volume(
    *,
    width: int,
    height: int,
    depth: int,
    seed: int | str = 0,
    octaves: int | None = None,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    amplitudes: Sequence[float] | None = None,
    independent_octaves: bool = False,
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
            amplitudes=amplitudes,
            independent_octaves=independent_octaves,
        ),
        width=width,
        height=height,
        depth=depth,
        start_x=start_x,
        start_y=start_y,
        start_z=start_z,
        step=step,
    )
