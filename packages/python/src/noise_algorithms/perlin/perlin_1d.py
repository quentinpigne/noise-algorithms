"""1D Perlin noise."""

from ..fractal_noise_generator import FractalNoiseGenerator
from ..sampling import sample_line
from ._base import PerlinNoise


class PerlinNoise1D(PerlinNoise):
    """1D Perlin noise generator (single octave)."""

    def noise(self, x: float) -> float:
        """Return a single octave of 1D Perlin noise at ``x`` in ``[-1, 1]``."""
        return self._octave(x)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        # 1D gradient: keep or mirror the displacement depending on the hash.
        d = displacement[0]
        return d if (h & 1) == 0 else -d


def perlin_1d(x: float, *, seed: int = 0) -> float:
    """One-shot single octave of 1D Perlin noise at ``x``.

    Builds a :class:`PerlinNoise1D` per call; reuse an instance for loops.
    """
    return PerlinNoise1D(seed=seed).noise(x)


def perlin_line(
    *,
    count: int,
    seed: int = 0,
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
        self._source = PerlinNoise1D(seed=seed)

    def _sample(self, *coords: float) -> float:
        return self._source.noise(*coords)

    def noise(self, x: float) -> float:
        """Return fractal 1D noise at ``x`` in the ``[-1, 1]`` interval."""
        return self._fractal(x)


def fractal_perlin_1d(
    x: float,
    *,
    seed: int = 0,
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
    seed: int = 0,
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
