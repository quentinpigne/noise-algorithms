"""Tests for the Perlin noise generators."""

import pytest

from noise_algorithms import (
    NoiseGenerator1D,
    NoiseGenerator2D,
    NoiseGenerator3D,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
    perlin_1d,
    perlin_2d,
    perlin_3d,
)

# Reference values captured from the implementation; guard against regressions.
SNAPSHOT_1D = -0.010612881309999999
SNAPSHOT_2D = 0.010676887276492134
SNAPSHOT_3D = 5.188027590892116e-06


def test_default_parameters():
    perlin = PerlinNoise2D()
    assert perlin._scale == 0.01
    assert perlin._octaves == 4
    assert perlin._lacunarity == 2.0
    assert perlin._persistence == 0.5


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
    perlin = PerlinNoise3D(seed=42, scale=0.1)
    for i in range(1000):
        for value in (
            PerlinNoise1D(seed=42, scale=0.1).noise(i * 0.37),
            PerlinNoise2D(seed=42, scale=0.1).noise(i * 0.37, i * 1.13),
            perlin.noise(i * 0.37, i * 1.13, i * 2.71),
        ):
            assert -1.0 <= value <= 1.0


def test_octaves_change_the_output():
    one = PerlinNoise2D(seed=42, octaves=1).noise(1.5, 2.5)
    many = PerlinNoise2D(seed=42, octaves=6).noise(1.5, 2.5)
    assert one != many


def test_functions_match_their_class():
    assert perlin_1d(1.5, seed=42) == PerlinNoise1D(seed=42).noise(1.5)
    assert perlin_2d(1.5, 2.5, seed=42) == PerlinNoise2D(seed=42).noise(1.5, 2.5)
    assert perlin_3d(1.5, 2.5, 3.5, seed=42) == PerlinNoise3D(seed=42).noise(
        1.5, 2.5, 3.5
    )


def test_generators_satisfy_their_protocol():
    assert isinstance(PerlinNoise1D(), NoiseGenerator1D)
    assert isinstance(PerlinNoise2D(), NoiseGenerator2D)
    assert isinstance(PerlinNoise3D(), NoiseGenerator3D)


def test_regression_snapshots():
    assert PerlinNoise1D(seed=42).noise(0.5) == pytest.approx(SNAPSHOT_1D, abs=1e-9)
    assert PerlinNoise2D(seed=42).noise(0.5, 0.5) == pytest.approx(
        SNAPSHOT_2D, abs=1e-9
    )
    assert PerlinNoise3D(seed=42).noise(0.5, 0.5, 0.5) == pytest.approx(
        SNAPSHOT_3D, abs=1e-9
    )
