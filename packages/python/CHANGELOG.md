# Changelog

All notable changes to the `noise-algorithms` Python package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-09-22

Same field, three times faster.

### Changed

- The bundled generators unroll their octave and their fractal loop per
  dimension instead of driving the dimension-agnostic engines. The generic
  engines rebuilt coordinate, offset and reduction lists on every call, and the
  fractal loop allocated a tuple per octave.

  Measured, best of five with the variants interleaved:

  | | 1.0.0 | 1.0.1 | |
  | --- | --- | --- | --- |
  | `PerlinNoise1D.noise` | 4043 ns | 1041 ns | ×3.9 |
  | `PerlinNoise2D.noise` | 7724 ns | 2333 ns | ×3.3 |
  | `PerlinNoise3D.noise` | 15310 ns | 4656 ns | ×3.3 |
  | `FractalPerlinNoise2D`, 4 octaves | 38818 ns | 10356 ns | ×3.7 |
  | `FractalPerlinNoise3D`, 4 octaves | 71779 ns | 20410 ns | ×3.5 |

  **The output is unchanged, bit-for-bit.** Same operations in the same order,
  so the same seed still produces the same field — including across languages.
  No migration: a world generated with 1.0.0 regenerates identically.

### Tests

- The cross-language conformance vectors are now asserted with `==` instead of
  `pytest.approx`. They carry the same-seed-same-field guarantee, and a tolerance
  could not express it: a one-ULP drift used to pass them.

### Notes for subclassers

`PerlinNoise._octave` / `_gradient` and `FractalNoiseGenerator._fractal` /
`_sample` are untouched, and still the way to add a dimension or a gradient set.
They are now also the specification the bundled fast paths are tested against,
bit-for-bit (`tests/test_octave_agreement.py`).

**But `noise` no longer routes through them on the bundled dimensions.** If you
derived `PerlinNoise2D` or `PerlinNoise3D` and overrode `_gradient` to bring
another gradient set — or `FractalPerlinNoise{1,2,3}D._sample` to stack another
source — that override is now ignored by `noise`, silently and without an error.
It still drives `_octave` / `_fractal`. To carry a gradient set of your own,
derive the abstract `PerlinNoise` and implement `noise` alongside `_gradient`.

The shared scale-and-clamp those fast paths end on is factored out as
`PerlinNoise._scaled(raw)`, carved out of the existing `_octave`.

## [1.0.0] - 2026-07-20

First public release. The same seed produces the same field as the TypeScript
package, and the output spans the full `[-1, 1]` range.

### Added

- Perlin noise in 1D/2D/3D, single-octave and fractal (fBm), each as a reusable
  class and a one-shot function:
  - single octave — `PerlinNoise{1,2,3}D` / `perlin_{1,2,3}d`
  - fractal — `FractalPerlinNoise{1,2,3}D` / `fractal_perlin_{1,2,3}d`
- Two abstract concepts with per-dimension protocols: `NoiseGenerator`
  (+ `NoiseGenerator{1,2,3}D`) and `FractalNoiseGenerator`
  (+ `FractalNoiseGenerator{1,2,3}D`).
- Region sampling — `sample_line` / `sample_grid` / `sample_volume` over any
  generator, plus per-algorithm one-shots (`perlin_grid`, `fractal_perlin_grid`,
  …).
- `to_unit_range` helper to remap output from `[-1, 1]` to `[0, 1]`.
- Keyword-only `seed` accepting an `int` or a `str` (hashed with FNV-1a, so
  named seeds like `"my-world"` work).
- Pure Python with no runtime dependencies (`numpy`/`matplotlib` are an optional
  `images` extra used only by the example). `src/` layout, `py.typed`, hatchling
  build backend. Requires Python 3.10 or newer.
