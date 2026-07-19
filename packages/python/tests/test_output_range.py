"""Tests for the output-range helper."""

from noise_algorithms import to_unit_range


def test_to_unit_range_maps_signed_to_unit():
    assert to_unit_range(-1) == 0.0
    assert to_unit_range(0) == 0.5
    assert to_unit_range(1) == 1.0
