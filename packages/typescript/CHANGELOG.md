# Changelog

All notable changes to `@quentinpigne/noise-algorithms` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-20

First public release. The same seed produces the same field as the Python
package, and the output spans the full `[-1, 1]` range.

### Added

- Perlin noise in 1D/2D/3D, single-octave and fractal (fBm), each as a reusable
  class and a one-shot function:
  - single octave — `PerlinNoise{1,2,3}D` / `perlin{1,2,3}D`
  - fractal — `FractalPerlinNoise{1,2,3}D` / `fractalPerlin{1,2,3}D`
- Two abstract concepts with per-dimension interfaces: `NoiseGenerator`
  (+ `NoiseGenerator{1,2,3}D`) and `FractalNoiseGenerator`
  (+ `FractalNoiseGenerator{1,2,3}D`).
- Region sampling — `sampleLine` / `sampleGrid` / `sampleVolume` over any
  generator, plus per-algorithm one-shots (`perlinGrid`, `fractalPerlinGrid`, …).
- `toUnitRange` helper to remap output from `[-1, 1]` to `[0, 1]`.
- Options-object constructors; the `seed` accepts a `number` or a `string`
  (hashed with FNV-1a, so named seeds like `"my-world"` work).
- ESM build with type declarations; entry points `.` (abstractions, interfaces,
  sampling helpers) and `/perlin-noise`. Requires Node.js ≥ 18.
