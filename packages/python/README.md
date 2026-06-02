# noise-algorithms (Python)

A collection of noise generation algorithms in **pure Python** (no runtime
dependencies). Part of the [noise-algorithms](https://github.com/quentinpigne/noise-algorithms)
monorepo.

## Preview

Perlin noise rendered from the built wheel (`seed=42`, `scale=0.03`) — these are
the snapshots the integration tests verify:

| 1D (signal graph) | 2D (field) | 3D (Swiss cheese cube) |
| :-: | :-: | :-: |
| ![1D](./tests/snapshots/perlin-noise-1d.png) | ![2D](./tests/snapshots/perlin-noise-2d.png) | ![3D](./tests/snapshots/perlin-noise-3d.png) |

## Installation

```sh
pip install noise-algorithms
```

## Usage

Two equivalent APIs are provided. Every generator returns fractal (multi-octave)
noise in the `[-1, 1]` interval.

### Classes (recommended for repeated sampling)

A class builds its permutation table once and reuses it across calls — use it
when generating many values (e.g. an image).

```python
from noise_algorithms import PerlinNoise1D, PerlinNoise2D, PerlinNoise3D

perlin = PerlinNoise2D(seed=42, scale=0.05, octaves=6)
for y in range(height):
    for x in range(width):
        value = perlin.noise(x, y)

PerlinNoise1D(seed=42).noise(3.0)
PerlinNoise3D(seed=42).noise(3.0, 4.0, 5.0)
```

### Functions (one-shot convenience)

The `perlin_*` functions wrap the classes for a single value. They build a
generator per call, so prefer a class instance for loops.

```python
from noise_algorithms import perlin_1d, perlin_2d, perlin_3d

perlin_2d(12.0, 7.0)                       # defaults
perlin_2d(12.0, 7.0, seed=42, scale=0.05)  # custom parameters
```

### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `seed` | `0` | Seed for the permutation table; same seed → same field. |
| `scale` | `0.01` | Base frequency multiplier applied to the coordinates. |
| `octaves` | `4` | Number of noise layers summed together. |
| `lacunarity` | `2.0` | Frequency multiplier between successive octaves. |
| `persistence` | `0.5` | Amplitude multiplier between successive octaves. |

The `noise_algorithms.NoiseGenerator{1,2,3}D` protocols describe the `noise`
contract if you want to type against it.

## Development

This package uses [uv](https://docs.astral.sh/uv/).

```sh
uv sync                 # install dev dependencies
uv run pytest           # unit + integration tests
uv run ruff check .     # lint
uv run ruff format .    # format
uv build                # build sdist + wheel
```

The integration test (`tests/integration/`) builds the wheel, imports it from an
isolated environment, renders a noise image and compares it to the committed
snapshot in `tests/snapshots/`; the rendered image is written to `tests/output/`.
Refresh the snapshot with `UPDATE_SNAPSHOTS=1 uv run pytest tests/integration`.

### Generating a preview image

```sh
uv run --extra images python examples/generate_images.py
```

## License

[MIT](./LICENSE)
