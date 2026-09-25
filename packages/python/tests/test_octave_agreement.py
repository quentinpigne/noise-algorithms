"""The unrolled octave must equal the generic engine, bit-for-bit.

The bundled dimensions unroll their octave and their fractal loop for speed, and
the generic engines they no longer run stay as the extension point.

Two implementations of the same maths is exactly the kind of drift the
cross-language invariant cannot survive, so it is pinned here: the fast path must
equal the generic one **bit-for-bit**, not merely to a tolerance. A rounding
difference is a field difference, and a field difference is a different world
from the same seed.

Mirrors ``packages/typescript/tests/octave-agreement.spec.ts``.
"""

import struct

import pytest

from noise_algorithms import (
    FractalPerlinNoise1D,
    FractalPerlinNoise2D,
    FractalPerlinNoise3D,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
)


def bits(value: float) -> bytes:
    """Raw bits of a float: two values that print alike can still differ."""
    return struct.pack(">d", value)


class Generic1D(PerlinNoise1D):
    """Exposes the generic engine, which ``noise`` no longer runs."""

    def generic(self, x: float) -> float:
        return self._octave(x)


class Generic2D(PerlinNoise2D):
    def generic(self, x: float, y: float) -> float:
        return self._octave(x, y)


class Generic3D(PerlinNoise3D):
    def generic(self, x: float, y: float, z: float) -> float:
        return self._octave(x, y, z)


class GenericFractal1D(FractalPerlinNoise1D):
    def generic(self, x: float) -> float:
        return self._fractal(x)


class GenericFractal2D(FractalPerlinNoise2D):
    def generic(self, x: float, y: float) -> float:
        return self._fractal(x, y)


class GenericFractal3D(FractalPerlinNoise3D):
    def generic(self, x: float, y: float, z: float) -> float:
        return self._fractal(x, y, z)


SEEDS = (0, 1, 42, "agreement", "ünïcødé")

# Fractional steps, both signs, and the cell borders the fade turns over.
COORDINATES = [(i - 30) * 0.37 for i in range(61)] + [
    0.0,
    -0.0,
    1.0,
    -1.0,
    255.0,
    256.0,
    -256.0,
    0.5,
    -0.5,
    1e6,
]


@pytest.mark.parametrize("seed", SEEDS)
def test_matches_in_1d_and_2d(seed: int | str) -> None:
    one = Generic1D(seed=seed)
    two = Generic2D(seed=seed)

    for x in COORDINATES:
        assert bits(one.noise(x)) == bits(one.generic(x))
        for y in COORDINATES[:12]:
            assert bits(two.noise(x, y)) == bits(two.generic(x, y))


@pytest.mark.parametrize("seed", SEEDS)
def test_matches_in_3d(seed: int | str) -> None:
    three = Generic3D(seed=seed)

    for x in COORDINATES:
        for y in COORDINATES[:8]:
            for z in COORDINATES[:5]:
                assert bits(three.noise(x, y, z)) == bits(three.generic(x, y, z))


# Every dimension unrolls its own stacking loop, so every dimension is pinned.
@pytest.mark.parametrize("octaves", [1, 2, 3, 7])
@pytest.mark.parametrize("lacunarity", [2.0, 1.87])
def test_matches_for_stacked_octaves(octaves: int, lacunarity: float) -> None:
    # Odd counts and non-default lacunarity: the loop must accumulate in the
    # same order, not just reach the same total.
    settings = {
        "seed": "agreement",
        "octaves": octaves,
        "lacunarity": lacunarity,
        "persistence": 0.43,
        "frequency": 0.017,
    }
    one = GenericFractal1D(**settings)
    two = GenericFractal2D(**settings)
    three = GenericFractal3D(**settings)

    for x in COORDINATES[:20]:
        assert bits(one.noise(x)) == bits(one.generic(x))
        assert bits(two.noise(x, x * 0.3)) == bits(two.generic(x, x * 0.3))
        assert bits(three.noise(x, x * 0.3, x * 0.7)) == bits(
            three.generic(x, x * 0.3, x * 0.7)
        )


# Weighted and independent octaves take their own loop: pin it too.
@pytest.mark.parametrize("independent_octaves", [False, True])
@pytest.mark.parametrize(
    "amplitudes", [[1.0], [1.0, 0.0, 2.0, 0.5], [0.0, 1.0, 1.0, 2.0, 2.0, 1.0]]
)
def test_matches_for_weighted_and_independent_octaves(
    amplitudes: list[float], independent_octaves: bool
) -> None:
    settings = {
        "seed": "agreement",
        "amplitudes": amplitudes,
        "independent_octaves": independent_octaves,
        "lacunarity": 2.0,
        "persistence": 0.5,
        "frequency": 0.013,
    }
    one = GenericFractal1D(**settings)
    two = GenericFractal2D(**settings)
    three = GenericFractal3D(**settings)

    for x in COORDINATES[:20]:
        assert bits(one.noise(x)) == bits(one.generic(x))
        assert bits(two.noise(x, x * 0.3)) == bits(two.generic(x, x * 0.3))
        assert bits(three.noise(x, x * 0.3, x * 0.7)) == bits(
            three.generic(x, x * 0.3, x * 0.7)
        )
