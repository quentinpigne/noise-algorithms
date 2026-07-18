"""Tests for the Perlin and fractal noise generators."""

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

# Reference values for fractal noise with the default parameters; captured from
# the implementation to guard against regressions.
SNAPSHOT_1D = -0.010612881309999999
SNAPSHOT_2D = 0.010676887276492134
SNAPSHOT_3D = 5.188027590892116e-06


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


@pytest.mark.parametrize(
    "call",
    [
        lambda seed: PerlinNoise1D(seed=seed).noise(1.5),
        lambda seed: PerlinNoise2D(seed=seed).noise(1.5, 2.5),
        lambda seed: PerlinNoise3D(seed=seed).noise(1.5, 2.5, 3.5),
    ],
)
def test_different_seeds_differ(call):
    assert call(1) != call(2)


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
    assert fractal_perlin_1d(0.5, seed=42) == pytest.approx(SNAPSHOT_1D, abs=1e-9)
    assert fractal_perlin_2d(0.5, 0.5, seed=42) == pytest.approx(SNAPSHOT_2D, abs=1e-9)
    assert fractal_perlin_3d(0.5, 0.5, 0.5, seed=42) == pytest.approx(
        SNAPSHOT_3D, abs=1e-9
    )
