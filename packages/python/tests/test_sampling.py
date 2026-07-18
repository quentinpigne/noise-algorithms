"""Tests for the region-sampling helpers."""

from noise_algorithms import (
    FractalPerlinNoise2D,
    PerlinNoise1D,
    PerlinNoise2D,
    PerlinNoise3D,
    fractal_perlin_grid,
    perlin_grid,
    perlin_line,
    perlin_volume,
    sample_grid,
    sample_line,
    sample_volume,
)


def test_sample_line_matches_noise_at_each_coordinate():
    gen = PerlinNoise1D(seed=42)
    line = sample_line(gen, count=5, start=2.0, step=0.5)
    assert len(line) == 5
    assert line == [gen.noise(2.0 + i * 0.5) for i in range(5)]


def test_sample_line_defaults():
    gen = PerlinNoise1D(seed=7)
    assert sample_line(gen, count=3) == [gen.noise(0), gen.noise(1), gen.noise(2)]


def test_sample_grid_shape_and_indexing():
    gen = FractalPerlinNoise2D(seed=42, frequency=0.05)
    grid = sample_grid(gen, width=3, height=2)
    assert len(grid) == 2  # rows
    assert all(len(row) == 3 for row in grid)  # columns
    for y in range(2):
        for x in range(3):
            assert grid[y][x] == gen.noise(x, y)


def test_sample_grid_origin_and_step():
    gen = PerlinNoise2D(seed=1)
    grid = sample_grid(gen, width=2, height=2, start_x=10, start_y=20, step=0.25)
    assert grid[1][0] == gen.noise(10, 20.25)
    assert grid[0][1] == gen.noise(10.25, 20)


def test_sample_volume_shape_and_indexing():
    gen = PerlinNoise3D(seed=42)
    volume = sample_volume(gen, width=2, height=3, depth=4)
    assert len(volume) == 4  # depth
    assert len(volume[0]) == 3  # height
    assert len(volume[0][0]) == 2  # width
    assert volume[3][2][1] == gen.noise(1, 2, 3)


def test_region_one_shots_match_building_a_generator_and_sampling_it():
    assert perlin_line(count=4, seed=7, step=0.5) == sample_line(
        PerlinNoise1D(seed=7), count=4, step=0.5
    )
    assert perlin_grid(width=3, height=2, seed=1) == sample_grid(
        PerlinNoise2D(seed=1), width=3, height=2
    )
    assert perlin_volume(width=2, height=2, depth=2, seed=2) == sample_volume(
        PerlinNoise3D(seed=2), width=2, height=2, depth=2
    )
    assert fractal_perlin_grid(
        width=4, height=4, seed=42, frequency=0.05
    ) == sample_grid(FractalPerlinNoise2D(seed=42, frequency=0.05), width=4, height=4)
