# Changelog

All notable changes to `@quentinpigne/noise-algorithms` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- 3D Perlin noise now selects all 12 gradient vectors (`h % 12` instead of the
  `h & 11` bitmask, which never reached vectors 4–7).
- A seed of `0` is treated as a valid, deterministic seed instead of falling
  back to a random one.

### Changed

- Reworked packaging for proper publication: `files` + `exports` (with a
  `./perlin-noise` entry point), complete npm metadata, and `main`/`module`/
  `types` pointing at the real build output. Removed the `prune-package-json`
  step.
- The dimension interfaces are re-exported as type-only.

### Added

- Unit tests for the interpolation and seeded-random utilities, plus regression
  tests for determinism, zero-seed handling and output bounds.
