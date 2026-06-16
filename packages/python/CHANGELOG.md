# Changelog

All notable changes to the `noise-algorithms` Python package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial pure-Python implementation of fractal Perlin noise, with two APIs
  mirroring the TypeScript package: the `PerlinNoise1D/2D/3D` classes (which
  build their permutation table once and are best for repeated sampling) and the
  `perlin_1d/2d/3d` one-shot convenience functions, plus `NoiseGenerator{1,2,3}D`
  typing protocols.
- Seeded permutation table built with the standard library (no runtime
  dependencies); `numpy`/`matplotlib` are an optional `images` extra used only
  by the example script.
- `src/` layout with a per-dimension `perlin` subpackage, `py.typed`, hatchling
  build backend and PyPI metadata.
- Requires Python 3.10 or newer.
- pytest suite (including an integration test that renders images from the built
  wheel and compares them to committed snapshots) and ruff lint/format configuration.
