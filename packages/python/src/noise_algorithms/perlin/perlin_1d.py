"""1D Perlin noise."""

from ..fractal_noise_generator import FractalNoiseGenerator
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
