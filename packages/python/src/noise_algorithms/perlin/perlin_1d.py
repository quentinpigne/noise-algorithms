"""1D Perlin noise."""

from ._base import PerlinNoise


class PerlinNoise1D(PerlinNoise):
    """1D Perlin noise generator."""

    def noise(self, x: float) -> float:
        """Return fractal 1D Perlin noise at ``x`` in the ``[-1, 1]`` interval."""
        return self._fractal(x)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        # 1D gradient: keep or mirror the displacement depending on the hash.
        d = displacement[0]
        return d if (h & 1) == 0 else -d


def perlin_1d(
    x: float,
    *,
    seed: int = 0,
    scale: float = 0.01,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """One-shot fractal 1D Perlin noise at ``x``.

    Convenience wrapper that builds a :class:`PerlinNoise1D` per call. For
    repeated sampling (e.g. rendering an image), instantiate
    :class:`PerlinNoise1D` once and reuse it.
    """
    generator = PerlinNoise1D(
        seed=seed,
        scale=scale,
        octaves=octaves,
        lacunarity=lacunarity,
        persistence=persistence,
    )
    return generator.noise(x)
