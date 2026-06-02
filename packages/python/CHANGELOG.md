# Changelog

All notable changes to the `noise-algorithms` Python package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial pure-Python implementation of fractal Perlin noise: `perlin_1d`,
  `perlin_2d`, `perlin_3d` and the `PerlinConfig` dataclass.
- Seeded permutation table built with the standard library (no runtime
  dependencies); `numpy`/`matplotlib` are an optional `images` extra used only
  by the example script.
- `src/` layout with `py.typed`, hatchling build backend and PyPI metadata.
- pytest suite and ruff lint/format configuration.
