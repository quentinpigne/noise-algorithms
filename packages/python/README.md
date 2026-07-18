# noise-algorithms (Python)

A collection of noise generation algorithms in **pure Python** (no runtime
dependencies). Part of the [noise-algorithms](https://github.com/quentinpigne/noise-algorithms)
monorepo.

## Preview

Perlin noise rendered from the built wheel (`seed=42`, `frequency=0.03`) — these are
the snapshots the integration tests verify:

| 1D (signal graph) | 2D (field) | 3D (Swiss cheese cube) |
| :-: | :-: | :-: |
| ![1D](./tests/snapshots/perlin-noise-1d.png) | ![2D](./tests/snapshots/perlin-noise-2d.png) | ![3D](./tests/snapshots/perlin-noise-3d.png) |

## Installation

```sh
pip install noise-algorithms
```

Requires Python 3.10 or newer; no runtime dependencies.

## Usage

Every generator returns noise in the `[-1, 1]` interval. Each algorithm offers
four entry points per dimension — a **class** (reuse it for repeated sampling)
and a one-shot **function** (builds a generator per call), in **single-octave**
and **fractal** flavours:

| | Class | Function |
| --- | --- | --- |
| Single octave | `PerlinNoise2D` | `perlin_2d(x, y, *, seed=0)` |
| Fractal (fBm) | `FractalPerlinNoise2D` | `fractal_perlin_2d(x, y, *, seed=0, ...)` |

```python
from noise_algorithms import (
    PerlinNoise2D,
    perlin_2d,
    FractalPerlinNoise2D,
    fractal_perlin_2d,
)

# Single octave
PerlinNoise2D(seed=42).noise(12, 7)
perlin_2d(12, 7, seed=42)

# Fractal (multi-octave)
FractalPerlinNoise2D(seed=42, octaves=6).noise(12, 7)
fractal_perlin_2d(12, 7, seed=42, octaves=6)
```

A class builds its permutation table once, so reuse an instance across calls
when generating many values (e.g. an image).

Fractal layering (fBm) is a **technique** for stacking octaves, not a noise
algorithm in itself. The shared octave-stacking engine lives in the abstract
`FractalNoiseGenerator` base (and the `FractalNoiseGenerator{1,2,3}D`
protocols); `FractalPerlinNoise2D` is the Perlin implementation. The base is
exported as an abstraction — there is no concrete generic wrapper to instantiate
with an arbitrary source.

### Parameters

A Perlin generator takes only `seed` (default `0`). A fractal generator takes
the layering options:

| Parameter | Default | Description |
| --- | --- | --- |
| `octaves` | `4` | Number of noise layers summed together. |
| `lacunarity` | `2.0` | Frequency multiplier between successive octaves. |
| `persistence` | `0.5` | Amplitude multiplier between successive octaves. |
| `frequency` | `0.01` | Base frequency applied to the first octave. |

The `FractalPerlinNoise{1,2,3}D` classes and `fractal_perlin_{1,2,3}d` functions
accept `seed` plus all of the above.

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
