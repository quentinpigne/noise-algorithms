# Changelog

All notable changes to the `noise-algorithms` Python package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
