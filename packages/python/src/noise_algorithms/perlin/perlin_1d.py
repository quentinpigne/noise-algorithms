"""1D Perlin noise."""

import math
from collections.abc import Sequence

from .._interpolation import fade, lerp
from .._octave_sources import OFFSET_AXES, octave_sources
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
            seed, self._octaves, independent_octaves, lambda s: PerlinNoise1D(seed=s)
        )

    def _sample(self, *coords: float, octave: int = 0) -> float:
        # Feeds the generic ``_fractal`` only — see :class:`FractalNoiseGenerator`.
        source = self._sources[octave]
        if not self._independent_octaves:
            return source.noise(*coords)
        at = octave * OFFSET_AXES
        return source.noise(coords[0] + self._offsets[at + 0])

    def noise(self, x: float) -> float:
        """Return fractal 1D noise at ``x`` in the ``[-1, 1]`` interval."""
        if self._independent_octaves:
            return self._independent_noise(x)

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
                value += source(x * frequency) * amplitudes[octave] * weight

        return value / self._amplitude_sum

    def _independent_noise(self, x: float) -> float:
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
                    sources[octave].noise(x * frequency + offsets[at + 0])
                    * amplitudes[octave]
                    * weight
                )

        return value / self._amplitude_sum


def fractal_perlin_1d(
    x: float,
    *,
    seed: int | str = 0,
    octaves: int | None = None,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    amplitudes: Sequence[float] | None = None,
    independent_octaves: bool = False,
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
        amplitudes=amplitudes,
        independent_octaves=independent_octaves,
    ).noise(x)


def fractal_perlin_line(
    *,
    count: int,
    seed: int | str = 0,
    octaves: int | None = None,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
    frequency: float = 0.01,
    amplitudes: Sequence[float] | None = None,
    independent_octaves: bool = False,
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
            amplitudes=amplitudes,
            independent_octaves=independent_octaves,
        ),
        count=count,
        start=start,
        step=step,
    )
