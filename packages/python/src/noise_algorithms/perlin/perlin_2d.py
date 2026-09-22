"""2D Perlin noise."""

import math

from .._interpolation import fade, lerp
from ..fractal_noise_generator import FractalNoiseGenerator
from ..sampling import sample_grid
from ._base import PerlinNoise

_UNIT = 1.0 / math.sqrt(2)

# 8 gradient directions, indexed with ``h & 7``.
_VECTORS = (
    (_UNIT, _UNIT),
    (-_UNIT, _UNIT),
    (_UNIT, -_UNIT),
    (-_UNIT, -_UNIT),
    (0.0, 1.0),
    (0.0, -1.0),
    (1.0, 0.0),
    (-1.0, 0.0),
)

#: The same table, flattened: ``_GRADIENTS[(h & 7) * 2 + axis]``.
_GRADIENTS = tuple(component for vector in _VECTORS for component in vector)


def _gradient(h: int, x: float, y: float) -> float:
    """Dot product of the hashed gradient with the corner displacement."""
    i = (h & 7) * 2
    return x * _GRADIENTS[i] + y * _GRADIENTS[i + 1]


class PerlinNoise2D(PerlinNoise):
    """2D Perlin noise generator (single octave)."""

    # Raw 2D gradient noise peaks at ±√2/2, so ×√2 fills [-1, 1].
    _NORMALIZATION = math.sqrt(2)

    def noise(self, x: float, y: float) -> float:
        """Return a single octave of 2D Perlin noise at ``(x, y)`` in ``[-1, 1]``."""
        p = self._permutation

        floor_x = math.floor(x)
        floor_y = math.floor(y)

        # Displacements from the low corner, and from the high one a unit away.
        low_x = x - floor_x
        low_y = y - floor_y
        high_x = low_x - 1
        high_y = low_y - 1

        u = fade(low_x)
        v = fade(low_y)

        x0 = floor_x & 255
        y0 = floor_y & 255
        x1 = (x0 + 1) & 255
        y1 = (y0 + 1) & 255

        # The permutation folds one axis at a time, so the prefixes are shared.
        px0 = p[x0]
        px1 = p[x1]

        # Interpolate along x, then y — the reduction order of the generic engine.
        y0_row = lerp(
            _gradient(p[p[px0 + y0]], low_x, low_y),
            _gradient(p[p[px1 + y0]], high_x, low_y),
            u,
        )
        y1_row = lerp(
            _gradient(p[p[px0 + y1]], low_x, high_y),
            _gradient(p[p[px1 + y1]], high_x, high_y),
            u,
        )

        return self._scaled(lerp(y0_row, y1_row, v))

    def _gradient(self, h: int, displacement: list[float]) -> float:
        # Feeds the generic ``_octave`` only — see :class:`PerlinNoise`.
        gx, gy = _VECTORS[h & 7]
        return displacement[0] * gx + displacement[1] * gy


def perlin_2d(x: float, y: float, *, seed: int | str = 0) -> float:
    """One-shot single octave of 2D Perlin noise at ``(x, y)``.

    Builds a :class:`PerlinNoise2D` per call; reuse an instance for loops.
    """
    return PerlinNoise2D(seed=seed).noise(x, y)


def perlin_grid(
    *,
    width: int,
    height: int,
    seed: int | str = 0,
    start_x: float = 0.0,
    start_y: float = 0.0,
    step: float = 1.0,
) -> list[list[float]]:
    """One-shot single octave of 2D Perlin noise over a regular grid — an image.

    Builds a :class:`PerlinNoise2D` and samples it with
    :func:`~noise_algorithms.sample_grid`.
    """
    return sample_grid(
        PerlinNoise2D(seed=seed),
        width=width,
        height=height,
        start_x=start_x,
        start_y=start_y,
        step=step,
    )


class FractalPerlinNoise2D(FractalNoiseGenerator):
    """Fractal (multi-octave) 2D Perlin noise.

    Stacks octaves of a :class:`PerlinNoise2D` source.
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
        self._source = PerlinNoise2D(seed=seed)

    def _sample(self, *coords: float) -> float:
        # Feeds the generic ``_fractal`` only — see :class:`FractalNoiseGenerator`.
        return self._source.noise(*coords)

    def noise(self, x: float, y: float) -> float:
        """Return fractal 2D noise at ``(x, y)`` in the ``[-1, 1]`` interval."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = self._frequency
        source = self._source.noise

        for _ in range(self._octaves):
            value += source(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value


def fractal_perlin_2d(
    x: float,
    y: float,
    *,
    seed: int | str = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
) -> float:
    """One-shot fractal 2D Perlin noise at ``(x, y)`` in ``[-1, 1]``.

    Builds a :class:`FractalPerlinNoise2D` per call; reuse an instance for loops.
    """
    return FractalPerlinNoise2D(
        seed=seed,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        frequency=frequency,
    ).noise(x, y)


def fractal_perlin_grid(
    *,
    width: int,
    height: int,
    seed: int | str = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    start_x: float = 0.0,
    start_y: float = 0.0,
    step: float = 1.0,
) -> list[list[float]]:
    """One-shot fractal 2D Perlin noise over a regular grid — an image.

    Builds a :class:`FractalPerlinNoise2D` and samples it with
    :func:`~noise_algorithms.sample_grid`.
    """
    return sample_grid(
        FractalPerlinNoise2D(
            seed=seed,
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
        ),
        width=width,
        height=height,
        start_x=start_x,
        start_y=start_y,
        step=step,
    )
