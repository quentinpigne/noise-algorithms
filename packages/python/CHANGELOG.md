# Changelog

All notable changes to the `noise-algorithms` Python package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-25

Weighted and independent octaves. Same field when you do not ask for them.

### Added

- **Weighted octaves.** The `amplitudes` option gives each octave a weight on
  top of the persistence curve: octave `i` weighs
  `amplitudes[i] × persistence^i`. `amplitudes=[1, 1, 2, 2, 2, 1]` lets a
  field favour a band of scales instead of following the persistence curve
  alone. A zero skips its octave, in the sum and in the divisor alike, and the
  sum is divided by the total of the absolute weights, so the output stays in
  `[-1, 1]`.
- **Independent octaves.** With `independent_octaves=True`, each octave draws
  its own permutation and a coordinate offset from the seed, instead of every
  octave sampling one source. A shared source repeats its lattice at every
  frequency, so all the layers cross zero together at the origin and wherever
  their lattices line up — visible in a field read against thresholds.
  Independent layers do not.
- Both options are accepted by the fractal classes, the one-shot functions and
  the region one-shots, and both combine.

### Cross-language invariant

- The octave draws are part of it: the seed drives xorshift32 and, for each
  octave in turn, one draw seeds its permutation, then three draws give its x, y
  and z offsets (`draw / 2³² × 256`) — three in every dimension. The same seed
  and options produce the same field in both packages, pinned by new conformance
  vectors asserted bit-for-bit in `tests/test_perlin.py` and shared with the
  TypeScript package.

### Validation

- `amplitudes` sets the number of octaves, so it is given **instead of**
  `octaves`, never with it: the two together raise `ValueError` rather than one
  silently winning. So do an empty list, a non-finite weight (`NaN`,
  `±Infinity`) and a list of zeros only.
- `octaves` now defaults to `None` rather than `4`, so that a count given
  alongside `amplitudes` can be told apart from the default. `None` still means
  four octaves: calls that pass `octaves` or leave it out behave as before.

### Compatibility

**Without the new options, the output is unchanged, bit-for-bit.** A weight of
`1` is exact, and the shared path does not add a zero offset, which could flip
the sign of a zero. The 1.0.1 conformance vectors and integration snapshots pass
unchanged: a world generated with 1.0.1 regenerates identically.

Plain fBm keeps its 1.0.1 speed. Each octave's frequency and amplitude, and the
divisor, are built once by the constructor — with the generic loop's running
products, in its order, so with the same bits — instead of on every call.

### Notes for subclassers

`FractalNoiseGenerator._sample` gains a keyword-only `octave`, passed only in
independent mode to select the source and its offset. A `_sample(*coords)`
override written for 1.0.1 keeps working for shared octaves.

The base class also gains `_weights`, `_independent_octaves`,
`_octave_frequencies`, `_octave_amplitudes` and `_amplitude_sum`, which a
subclass setting attributes of the same name would overwrite.

The generic `_fractal` is still the specification the bundled loops are tested
against, bit-for-bit, now for weighted and independent octaves too
(`tests/test_octave_agreement.py`).

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
