"""Abstract base for fractal (fBm) noise generators.

Fractal noise is not a noise algorithm in itself but a *technique* for stacking
octaves of a source noise: each octave samples the source at an increasing
frequency and decreasing amplitude, and the contributions are summed and
normalised back into the ``[-1, 1]`` interval. This dimension- and
source-agnostic engine lives here; subclasses bind a concrete source and adapt
its ``noise(...)`` signature via ``_sample``.
"""

from abc import ABC, abstractmethod


class FractalNoiseGenerator(ABC):
    """Layers octaves of a source noise generator (fractal Brownian motion).

    Args:
        octaves: Number of noise layers summed together.
        lacunarity: Frequency multiplier between successive octaves.
        persistence: Amplitude multiplier between successive octaves.
        frequency: Base frequency applied to the coordinates of the first octave.
    """

    def __init__(
        self,
        *,
        octaves: int = 4,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
        frequency: float = 0.01,
    ) -> None:
        self._octaves = octaves
        self._lacunarity = lacunarity
        self._persistence = persistence
        self._frequency = frequency

    def _fractal(self, *coords: float) -> float:
        """Sum ``octaves`` layers of the source noise; result is in ``[-1, 1]``."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = self._frequency

        for _ in range(self._octaves):
            scaled = tuple(c * frequency for c in coords)
            value += self._sample(*scaled) * amplitude
            max_value += amplitude
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value

    @abstractmethod
    def _sample(self, *coords: float) -> float:
        """Sample the wrapped source generator at the given coordinates."""
