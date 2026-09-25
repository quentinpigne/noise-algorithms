# Changelog

All notable changes to `@quentinpigne/noise-algorithms` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Weighted octaves**: the `amplitudes` option gives each octave a weight on
  top of the persistence curve — octave `i` weighs
  `amplitudes[i] × persistence^i` — and sets the number of octaves, so it cannot
  be given with `octaves`. A zero skips its octave; the weights must be finite.
- **Independent octaves**: with `independentOctaves: true`, each octave draws
  its own permutation and a coordinate offset from the seed, instead of all
  sampling one source. The layers no longer cross zero together at the origin
  and along their shared lattice.
- Both are optional and additive: without them, every generator returns the
  same bits as before. The octave draws are part of the cross-language
  invariant, pinned by new conformance vectors shared with the Python package.

## [1.0.1] - 2026-09-22

Same field, eleven times faster.

### Changed

- The bundled generators unroll their octave and their fractal loop per
  dimension instead of driving the dimension-agnostic engines. The generic
  engines carried coordinates, corner offsets and intermediate reductions in
  arrays — sixteen allocations for one 3D call, one more per fractal octave —
  which cost more than the arithmetic they performed.

  Measured, best of three after warm-up:

  |                                   | 1.0.0    | 1.0.1   |       |
  | --------------------------------- | -------- | ------- | ----- |
  | `PerlinNoise2D.noise`             | 1408 ns  | 122 ns  | ×11.5 |
  | `PerlinNoise3D.noise`             | 2814 ns  | 248 ns  | ×11.3 |
  | `FractalPerlinNoise3D`, 4 octaves | 11701 ns | 1029 ns | ×11.4 |

  **The output is unchanged, bit-for-bit.** Same operations in the same order,
  so the same seed still produces the same field — including across languages.
  No migration: a world generated with 1.0.0 regenerates identically.

### Tests

- The cross-language conformance vectors are now asserted with `toBe` instead of
  `toBeCloseTo`. They carry the same-seed-same-field guarantee, and a tolerance
  could not express it: a one-ULP drift used to pass them.

### Notes for subclassers

`PerlinNoise.octave` / `gradient` and `FractalNoiseGenerator.fractal` / `sample`
are untouched, and still the way to add a dimension or a gradient set. They are
now also the specification the bundled fast paths are tested against,
bit-for-bit.

**But `noise` no longer routes through them on the bundled dimensions.** If you
subclassed `PerlinNoise2D` or `PerlinNoise3D` and overrode `gradient` to bring
another gradient set — or `FractalPerlinNoise{1,2,3}D.sample` to stack another
source — that override is now ignored by `noise`, silently and without an error.
It still drives `octave` / `fractal`. To carry a gradient set of your own, extend
the abstract `PerlinNoise` and implement `noise` alongside `gradient`.

Nothing in the bundled API changed shape, which is why this is a patch; but a
subclass that relied on the old dispatch produces different values, and that
deserves reading before upgrading.

The shared scale-and-clamp those fast paths end on is factored out as
`PerlinNoise.scaled(raw)` — a `protected` helper carved out of the existing
`octave`, not a new capability. It is noted here so its arrival has a date, not
because it changes what the package offers.

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
