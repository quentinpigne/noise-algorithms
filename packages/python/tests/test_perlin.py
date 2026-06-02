"""Tests for the Perlin noise generators."""

from dataclasses import FrozenInstanceError

import pytest

from noise_algorithms import PerlinConfig, perlin_1d, perlin_2d, perlin_3d


def test_config_defaults():
    config = PerlinConfig()
    assert config.seed == 0
    assert config.scale == 0.01
    assert config.octaves == 4
    assert config.lacunarity == 2.0
    assert config.persistence == 0.5


def test_config_is_immutable():
    config = PerlinConfig()
    with pytest.raises(FrozenInstanceError):
        config.seed = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    "call",
    [
        lambda c: perlin_1d(1.5, c),
        lambda c: perlin_2d(1.5, 2.5, c),
        lambda c: perlin_3d(1.5, 2.5, 3.5, c),
    ],
)
def test_deterministic_for_a_given_seed(call):
    config = PerlinConfig(seed=42)
    assert call(config) == call(config)


@pytest.mark.parametrize(
    "call",
    [
        lambda c: perlin_1d(1.5, c),
        lambda c: perlin_2d(1.5, 2.5, c),
        lambda c: perlin_3d(1.5, 2.5, 3.5, c),
    ],
)
def test_different_seeds_differ(call):
    assert call(PerlinConfig(seed=1)) != call(PerlinConfig(seed=2))


def test_seed_zero_is_valid_and_deterministic():
    config = PerlinConfig(seed=0)
    assert perlin_2d(1.5, 2.5, config) == perlin_2d(1.5, 2.5, config)


def test_output_within_bounds():
    config = PerlinConfig(seed=42, scale=0.1)
    for i in range(1000):
        for value in (
            perlin_1d(i * 0.37, config),
            perlin_2d(i * 0.37, i * 1.13, config),
            perlin_3d(i * 0.37, i * 1.13, i * 2.71, config),
        ):
            assert -1.0 <= value <= 1.0


def test_default_config_used_when_omitted():
    assert perlin_2d(1.5, 2.5) == perlin_2d(1.5, 2.5, PerlinConfig())


def test_octaves_change_the_output():
    one = perlin_2d(1.5, 2.5, PerlinConfig(seed=42, octaves=1))
    many = perlin_2d(1.5, 2.5, PerlinConfig(seed=42, octaves=6))
    assert one != many


def test_regression_snapshots():
    config = PerlinConfig(seed=42)
    assert perlin_1d(0.5, config) == pytest.approx(__SNAP_1D, abs=1e-9)
    assert perlin_2d(0.5, 0.5, config) == pytest.approx(__SNAP_2D, abs=1e-9)
    assert perlin_3d(0.5, 0.5, 0.5, config) == pytest.approx(__SNAP_3D, abs=1e-9)


# Reference values captured from the implementation; guard against regressions.
__SNAP_1D = -0.010612881309999999
__SNAP_2D = 0.010676887276492134
__SNAP_3D = 5.188027590892116e-06
