"""Tests for the Perlin and fractal noise generators."""

import math

import pytest

from noise_algorithms import (
    FractalNoiseGenerator,
    FractalNoiseGenerator1D,
    FractalNoiseGenerator2D,
    FractalNoiseGenerator3D,
    FractalPerlinNoise1D,
    FractalPerlinNoise2D,
    FractalPerlinNoise3D,
    NoiseGenerator,
    NoiseGenerator1D,
    NoiseGenerator2D,
    NoiseGenerator3D,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
    fractal_perlin_1d,
    fractal_perlin_2d,
    fractal_perlin_3d,
    perlin_1d,
    perlin_2d,
    perlin_3d,
)

# Cross-language conformance vectors: these exact values are also asserted in
# the TypeScript suite (perlin-noise.spec.ts). The same seed must produce the
# same field in every package — keep the two lists identical.
#
# They are asserted with `==`, not a tolerance. The invariant these vectors guard
# is bit-for-bit identity, and a tolerance cannot express it: at `abs=1e-9` a
# value may drift by seven orders of magnitude more than an ULP and still pass,
# so the assertion would agree while the field quietly differed. Each literal is
# the shortest decimal that round-trips to its f64, and parses to the same bits
# in Python and in JavaScript — verified against the raw bytes.
SNAPSHOT_1D = -0.02143353418166667  # bf95f2ac21644eb3
SNAPSHOT_2D = 2.338095654778e-5  # 3ef88447197c25d4
SNAPSHOT_3D = 0.021326036454289054  # 3f95d67e147f7673


def test_fractal_default_parameters():
    fractal = FractalPerlinNoise2D()
    assert fractal._frequency == 0.01
    assert fractal._octaves == 4
    assert fractal._lacunarity == 2.0
    assert fractal._persistence == 0.5


@pytest.mark.parametrize(
    "call",
    [
        lambda seed: PerlinNoise1D(seed=seed).noise(1.5),
        lambda seed: PerlinNoise2D(seed=seed).noise(1.5, 2.5),
        lambda seed: PerlinNoise3D(seed=seed).noise(1.5, 2.5, 3.5),
    ],
)
def test_deterministic_for_a_given_seed(call):
    assert call(42) == call(42)


# A single octave can coincide at a symmetric point (e.g. cell centres) for two
# seeds, so sample several off-lattice points and compare the sequences.
@pytest.mark.parametrize(
    "samples",
    [
        lambda seed: [PerlinNoise1D(seed=seed).noise(x) for x in (0.3, 1.3, 4.2)],
        lambda seed: [
            PerlinNoise2D(seed=seed).noise(x, y)
            for x, y in ((0.3, 0.7), (1.3, 2.7), (4.2, 1.8))
        ],
        lambda seed: [
            PerlinNoise3D(seed=seed).noise(x, y, z)
            for x, y, z in ((0.3, 0.7, 1.1), (1.3, 2.7, 0.4), (4.2, 1.8, 3.6))
        ],
    ],
)
def test_different_seeds_differ(samples):
    assert samples(1) != samples(2)


def test_seed_zero_is_valid_and_deterministic():
    assert PerlinNoise2D(seed=0).noise(1.5, 2.5) == PerlinNoise2D(seed=0).noise(
        1.5, 2.5
    )


def test_output_within_bounds():
    perlin = PerlinNoise3D(seed=42)
    fractal = FractalPerlinNoise3D(seed=42, frequency=0.1)
    for i in range(1000):
        for value in (
            PerlinNoise1D(seed=42).noise(i * 0.37),
            PerlinNoise2D(seed=42).noise(i * 0.37, i * 1.13),
            perlin.noise(i * 0.37, i * 1.13, i * 2.71),
            fractal.noise(i * 0.37, i * 1.13, i * 2.71),
        ):
            assert -1.0 <= value <= 1.0


def test_octaves_change_the_output():
    one = FractalPerlinNoise2D(seed=42, octaves=1).noise(1.5, 2.5)
    many = FractalPerlinNoise2D(seed=42, octaves=6).noise(1.5, 2.5)
    assert one != many


def test_simple_functions_match_their_class():
    assert perlin_1d(1.5, seed=42) == PerlinNoise1D(seed=42).noise(1.5)
    assert perlin_2d(1.5, 2.5, seed=42) == PerlinNoise2D(seed=42).noise(1.5, 2.5)
    assert perlin_3d(1.5, 2.5, 3.5, seed=42) == PerlinNoise3D(seed=42).noise(
        1.5, 2.5, 3.5
    )


def test_fractal_functions_match_their_class():
    assert fractal_perlin_1d(1.5, seed=42) == FractalPerlinNoise1D(seed=42).noise(1.5)
    assert fractal_perlin_2d(1.5, 2.5, seed=42) == FractalPerlinNoise2D(seed=42).noise(
        1.5, 2.5
    )
    assert fractal_perlin_3d(1.5, 2.5, 3.5, seed=42) == FractalPerlinNoise3D(
        seed=42
    ).noise(1.5, 2.5, 3.5)


def test_generators_satisfy_their_protocol():
    assert isinstance(PerlinNoise1D(), NoiseGenerator1D)
    assert isinstance(PerlinNoise2D(), NoiseGenerator2D)
    assert isinstance(PerlinNoise3D(), NoiseGenerator3D)
    assert isinstance(FractalPerlinNoise1D(), FractalNoiseGenerator1D)
    assert isinstance(FractalPerlinNoise2D(), FractalNoiseGenerator2D)
    assert isinstance(FractalPerlinNoise3D(), FractalNoiseGenerator3D)
    # A fractal generator is still a noise generator.
    assert isinstance(FractalPerlinNoise2D(), NoiseGenerator2D)


def test_implementations_extend_the_abstract_concepts():
    assert issubclass(PerlinNoise2D, NoiseGenerator)
    assert issubclass(FractalPerlinNoise2D, FractalNoiseGenerator)


def test_regression_snapshots():
    assert fractal_perlin_1d(0.5, seed=42) == SNAPSHOT_1D
    assert fractal_perlin_2d(0.5, 0.5, seed=42) == SNAPSHOT_2D
    assert fractal_perlin_3d(0.5, 0.5, 0.5, seed=42) == SNAPSHOT_3D


# Cross-language conformance vector: also asserted in the TypeScript suite. A
# string seed is hashed (FNV-1a) to an integer, identically in every package.
# Exact, for the same reason as the vectors above.
STRING_SEED_SNAPSHOT = -0.01500367218449442  # bf8eba3ecad18713


def test_string_seed_hashes_to_a_deterministic_field():
    assert fractal_perlin_2d(0.5, 0.5, seed="hello") == STRING_SEED_SNAPSHOT


def test_different_string_seeds_differ():
    assert fractal_perlin_2d(1.5, 2.5, seed="alpha") != fractal_perlin_2d(
        1.5, 2.5, seed="beta"
    )


# Cross-language conformance vectors for weighted and independent octaves, also
# asserted in perlin-noise.spec.ts: the octave sources are drawn from the seed
# in a fixed order, and both packages must draw the same ones.
INDEPENDENT = {
    "seed": 42,
    "amplitudes": [1, 2, 0, 1],
    "independent_octaves": True,
    "frequency": 0.25,
}


def test_independent_octaves_conformance():
    assert (
        fractal_perlin_1d(0.5, **INDEPENDENT) == 0.060837062084114574
    )  # 3faf260910126dc4
    assert (
        fractal_perlin_2d(0.5, 0.5, **INDEPENDENT) == 0.33682886946882246
    )  # 3fd58e9aacade759
    assert (
        fractal_perlin_3d(0.5, 0.5, 0.5, **INDEPENDENT) == -0.01860693052720046
    )  # bf930db1f85f822d


def test_weighted_shared_octaves_conformance():
    value = fractal_perlin_2d(
        0.5, 0.5, seed=42, amplitudes=[1, 2, 0, 1], frequency=0.25
    )
    assert value == 0.033605902542557374  # 3fa134caf8bee5d3


def test_independent_octaves_do_not_cross_zero_at_the_origin():
    # A shared source is zero on its lattice, the origin first; offset octaves
    # are not.
    assert fractal_perlin_3d(0, 0, 0, seed="monde") == 0
    value = fractal_perlin_3d(0, 0, 0, seed="monde", independent_octaves=True)
    assert value == -0.15382253414265762  # bfc3b074f0c3e952


def test_unit_weights_keep_plain_fbm():
    for x, y in [(1.5, 2.5), (-7.25, 3.125)]:
        weighted = FractalPerlinNoise2D(seed=9, amplitudes=[1, 1, 1]).noise(x, y)
        plain = FractalPerlinNoise2D(seed=9, octaves=3).noise(x, y)
        assert weighted == plain


def test_zero_weight_skips_its_octave():
    # A zero drops the octave from the sum and from the normalisation alike.
    skipped = FractalPerlinNoise2D(seed=9, amplitudes=[1, 0]).noise(1.5, 2.5)
    assert skipped == FractalPerlinNoise2D(seed=9, octaves=1).noise(1.5, 2.5)


def test_refuses_octaves_and_amplitudes_together():
    # `amplitudes` sets the number of octaves: a second count would conflict.
    with pytest.raises(ValueError):
        FractalPerlinNoise2D(amplitudes=[1, 1], octaves=2)


def test_weighted_independent_output_within_bounds():
    noise = FractalPerlinNoise3D(
        seed=3,
        amplitudes=[1, 1, 2, 2, 2, 1, 1, 1, 1],
        independent_octaves=True,
        frequency=0.01,
    )
    for i in range(1000):
        assert -1 <= noise.noise(i * 3.7, i * 1.3, i * 2.9) <= 1


def test_independent_octaves_differ_from_the_shared_field():
    options = {"seed": "det", "independent_octaves": True, "octaves": 5}
    a = FractalPerlinNoise2D(**options).noise(12.3, 45.6)
    assert a == FractalPerlinNoise2D(**options).noise(12.3, 45.6)
    assert a != FractalPerlinNoise2D(seed="det", octaves=5).noise(12.3, 45.6)


@pytest.mark.parametrize("amplitudes", [[], [0, 0], [1, math.nan], [1, math.inf]])
def test_refuses_amplitudes_it_cannot_honour(amplitudes):
    with pytest.raises(ValueError):
        FractalPerlinNoise2D(amplitudes=amplitudes)
