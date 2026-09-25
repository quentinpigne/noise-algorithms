"""Abstract base for fractal (fBm) noise generators.

Fractal noise is not a noise algorithm in itself but a *technique* for stacking
octaves of a source noise: each octave samples the source at an increasing
frequency and decreasing amplitude, and the contributions are summed and
normalised back into the ``[-1, 1]`` interval. This dimension- and
source-agnostic engine lives here; subclasses bind a concrete source and adapt
its ``noise(...)`` signature via ``_sample``.

**The bundled dimensions do not run it.** Passing coordinates as a tuple means an
allocation per octave, and the attribute lookups repeat on every layer;
``FractalPerlinNoise{1,2,3}D`` each write their own loop. ``_fractal`` stays as
the extension point and as the specification the unrolled loops are tested
against.
"""

import math
from abc import ABC, abstractmethod
from collections.abc import Sequence


class FractalNoiseGenerator(ABC):
    """Layers octaves of a source noise generator (fractal Brownian motion).

    Args:
        octaves: Number of noise layers summed together. Defaults to ``4``, or
            to the length of ``amplitudes``, which cannot be given with it.
        lacunarity: Frequency multiplier between successive octaves.
        persistence: Amplitude multiplier between successive octaves.
        frequency: Base frequency applied to the coordinates of the first octave.
        amplitudes: Weight of each octave, on top of the persistence curve:
            octave ``i`` contributes ``amplitudes[i] * persistence**i``. Its
            length is the number of octaves, so it cannot be given with
            ``octaves``; a zero skips its octave. The weights must be finite,
            and at least one non-zero. Defaults to a weight of ``1`` for every
            octave — plain fBm.
        independent_octaves: Give every octave its own permutation and its own
            coordinate offset, drawn from the seed, instead of sampling one
            source at every frequency. One shared source repeats its lattice at
            every octave, and they all cross zero together where the lattices
            line up. Defaults to ``False``.
    """

    def __init__(
        self,
        *,
        octaves: int | None = None,
        lacunarity: float = 2.0,
        persistence: float = 0.5,
        frequency: float = 0.01,
        amplitudes: Sequence[float] | None = None,
        independent_octaves: bool = False,
    ) -> None:
        self._weights = _weights_of(octaves, amplitudes)
        self._octaves = len(self._weights)
        self._lacunarity = lacunarity
        self._persistence = persistence
        self._frequency = frequency
        self._independent_octaves = independent_octaves

        # The frequency and amplitude of each octave, and the sum the stacked
        # value is divided by. They do not depend on the coordinates, so the
        # unrolled loops read them instead of recomputing them on every call;
        # they are built with the operations of the generic ``_fractal`` loop, in
        # its order, so they hold the same bits.
        self._octave_frequencies: list[float] = []
        self._octave_amplitudes: list[float] = []
        amplitude = 1.0
        frequency = self._frequency
        amplitude_sum = 0.0
        for weight in self._weights:
            self._octave_frequencies.append(frequency)
            self._octave_amplitudes.append(amplitude)
            if weight != 0:
                amplitude_sum += amplitude * abs(weight)
            amplitude *= self._persistence
            frequency *= self._lacunarity
        self._amplitude_sum = amplitude_sum

    def _fractal(self, *coords: float) -> float:
        """Sum ``octaves`` layers of the source noise; result is in ``[-1, 1]``."""
        value = 0.0
        max_value = 0.0
        amplitude = 1.0
        frequency = self._frequency

        for octave in range(self._octaves):
            weight = self._weights[octave]
            if weight != 0:
                scaled = tuple(c * frequency for c in coords)
                # The octave is passed only when it selects a source: a subclass
                # written before independent octaves keeps its `_sample(*coords)`.
                sample = (
                    self._sample(*scaled, octave=octave)
                    if self._independent_octaves
                    else self._sample(*scaled)
                )
                value += sample * amplitude * weight
                max_value += amplitude * abs(weight)
            amplitude *= self._persistence
            frequency *= self._lacunarity

        return value / max_value

    @abstractmethod
    def _sample(self, *coords: float, octave: int = 0) -> float:
        """Sample the wrapped source generator at the given coordinates.

        With independent octaves, ``octave`` selects the source and its offset;
        a shared source is sampled as is, so plain fBm keeps its exact bits.

        **Feeds the generic ``_fractal`` only.** ``noise`` stacks its own
        octaves, so overriding this method does *not* change what ``noise``
        returns. To stack a different source, derive
        :class:`FractalNoiseGenerator` directly and implement ``noise``
        alongside ``_sample``.
        """


def _weights_of(octaves: int | None, amplitudes: Sequence[float] | None) -> list[float]:
    """The octave weights the options ask for.

    A weight of ``1`` is exact in floating point, so plain fBm computes the same
    bits with or without this step.
    """
    if amplitudes is None:
        return [1.0] * (4 if octaves is None else octaves)

    if octaves is not None:
        raise ValueError(
            "give octaves or amplitudes, not both: "
            "amplitudes sets the number of octaves"
        )
    if len(amplitudes) == 0:
        raise ValueError("amplitudes must name at least one octave")
    if not all(math.isfinite(weight) for weight in amplitudes):
        raise ValueError("amplitudes must be finite numbers")
    if all(weight == 0 for weight in amplitudes):
        raise ValueError("amplitudes must have at least one non-zero weight")
    return list(amplitudes)
