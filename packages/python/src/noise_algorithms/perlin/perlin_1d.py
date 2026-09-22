"""1D Perlin noise."""

import math

from .._interpolation import fade, lerp
from ..fractal_noise_generator import FractalNoiseGenerator
from ..sampling import sample_line
from ._base import PerlinNoise


class PerlinNoise1D(PerlinNoise):
    """1D Perlin noise generator (single octave)."""

    # Raw 1D gradient noise peaks at ±0.5, so ×2 fills [-1, 1].
    _NORMALIZATION = 2.0

    def noise(self, x: float) -> float:
        """Return a single octave of 1D Perlin noise at ``x`` in ``[-1, 1]``."""
        p = self._permutation

        floor_x = math.floor(x)
        low_x = x - floor_x
        high_x = low_x - 1
        u = fade(low_x)

        x0 = floor_x & 255
        x1 = (x0 + 1) & 255

        # In one dimension the gradient is a sign: the hash keeps or mirrors
        # the displacement.
        hash_0 = p[p[x0]]
        hash_1 = p[p[x1]]
        low = low_x if (hash_0 & 1) == 0 else -low_x
        high = high_x if (hash_1 & 1) == 0 else -high_x

        return self._scaled(lerp(low, high, u))

    def _gradient(self, h: int, displacement: list[float]) -> float:
        # 1D gradient: keep or mirror the displacement depending on the hash.
        # Feeds the generic ``_octave`` only — see :class:`PerlinNoise`.
        d = displacement[0]
        return d if (h & 1) == 0 else -d


def perlin_1d(x: float, *, seed: int | str = 0) -> float:
    """One-shot single octave of 1D Perlin noise at ``x``.

    Builds a :class:`PerlinNoise1D` per call; reuse an instance for loops.
    """
    return PerlinNoise1D(seed=seed).noise(x)


def perlin_line(
    *,
    count: int,
    seed: int | str = 0,
    start: float = 0.0,
    step: float = 1.0,
) -> list[float]:
    """One-shot single octave of 1D Perlin noise over a regular interval — a curve.

    Builds a :class:`PerlinNoise1D` and samples it with
    :func:`~noise_algorithms.sample_line`.
    """
    return sample_line(PerlinNoise1D(seed=seed), count=count, start=start, step=step)


class FractalPerlinNoise1D(FractalNoiseGenerator):
    """Fractal (multi-octave) 1D Perlin noise.

    Stacks octaves of a :class:`PerlinNoise1D` source.
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
        self._source = PerlinNoise1D(seed=seed)

    def _sample(self, *coords: float) -> float:
        # Feeds the generic ``_fractal`` only — see :class:`FractalNoiseGenerator`.
        return self._source.noise(*coords)

    def noise(self, x: float) -> float:
        """Return fractal 1D noise at ``x`` in the ``[-1, 1]`` interval."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = self._frequency
        source = self._source.noise

        for _ in range(self._octaves):
            value += source(x * frequency) * amplitude
            max_value += amplitude
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value


def fractal_perlin_1d(
    x: float,
    *,
    seed: int | str = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
) -> float:
    """One-shot fractal 1D Perlin noise at ``x`` in ``[-1, 1]``.

    Builds a :class:`FractalPerlinNoise1D` per call; reuse an instance for loops.
    """
    return FractalPerlinNoise1D(
        seed=seed,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
        frequency=frequency,
    ).noise(x)


def fractal_perlin_line(
    *,
    count: int,
    seed: int | str = 0,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    start: float = 0.0,
    step: float = 1.0,
) -> list[float]:
    """One-shot fractal 1D Perlin noise over a regular interval — a curve.

    Builds a :class:`FractalPerlinNoise1D` and samples it with
    :func:`~noise_algorithms.sample_line`.
    """
    return sample_line(
        FractalPerlinNoise1D(
            seed=seed,
            octaves=octaves,
            lacunarity=lacunarity,
            persistence=persistence,
            frequency=frequency,
        ),
        count=count,
        start=start,
        step=step,
    )
