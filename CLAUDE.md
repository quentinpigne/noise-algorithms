# CLAUDE.md — noise-algorithms

Polyglot monorepo: the same noise algorithms implemented as idiomatic, **independently
versioned** libraries, one per language under `packages/<lang>`. Currently
TypeScript (npm) and Python (PyPI); a Rust crate is scaffolded on the
`feat/rust-crate-scaffold` branch.

Per-package dev details live in `packages/<lang>/CLAUDE.md`. This file covers what
is true across the whole repo.

## ⚠️ The one invariant that must never break

**The same seed must produce the same field, bit-for-bit, in every language.**
This is a headline guarantee, locked by **shared conformance vectors** duplicated
in each test suite (`perlin-noise.spec.ts` ↔ `test_perlin.py`) — the exact same
numeric literals in both, asserted with `toBe` / `==` and never a tolerance,
because a tolerance cannot express a bit-for-bit invariant.

The shared, portable spec (all designed to be reproducible with 32-bit integer
ops and standard IEEE-754 `f64`):

- **PRNG**: `xorshift32` (masked 32-bit int ops).
- **String seeds**: hashed to a `uint32` with **FNV-1a** over UTF-8 bytes.
- **Permutation**: Fisher-Yates with integer-modulo index, seeded by xorshift32.
- **Gradients**: 2D `hash & 7` (8 vectors); 3D `hash & 15` (16-entry table = 12
  edges + 4 balanced duplicates, avoids the `% 12` modulo bias). Unit-length.
- **Normalization**: each octave × per-dimension factor (`[2, √2, √2]`) then
  clamped, so output fills `[-1, 1]`.
- **`fade` / `lerp`**, the octave's corner/reduction arithmetic, and the fractal
  loop — identical **order of operations**. The *shape* of the code is not
  normative: TypeScript unrolls both per dimension for speed (see below), Python
  keeps the generic loops, and the two agree bit-for-bit.

**Unrolled in both packages.** Each writes the octave and the fractal loop out
per dimension rather than driving them with the dimension-agnostic engine. A
generic engine carries coordinates, corner offsets and intermediate reductions in
arrays — sixteen allocations per 3D call — which cost eleven times the arithmetic
it performed in TypeScript and a little over three times in Python. Same
operations, same order, same values; only the allocations are gone.

**The generic engines stay**, in both languages: they are the extension point a
new dimension or gradient set builds on, and they are also the executable
specification — `octave-agreement.spec.ts` and `test_octave_agreement.py` pin the
unrolled path to the generic one **bit-for-bit**, so the two cannot drift. Two
implementations of the same maths is precisely what this invariant cannot survive
unguarded, and there are now four.

**`gradient` / `_gradient` and `sample` / `_sample` on the bundled dimensions no
longer feed `noise`** — they feed the generic engine, which is to say the
agreement tests. Overriding them on `PerlinNoise3D` or `FractalPerlinNoise3D` is
silently ignored. A new gradient set derives the abstract `PerlinNoise` and
implements `noise` alongside it.

If you touch ANY of the above, you must: mirror it in **both** packages, keep the
op-order identical (f64 determinism), regenerate the golden vectors + integration
snapshots, and re-confirm cross-language identity. When porting to a new language,
watch the subtle traps — e.g. `UNIT = 1.0 / sqrt(2)` must be **computed**, not a
built-in `FRAC_1_SQRT_2`-style constant (they can differ by an ULP); no FMA
fusion. A throwaway conformance spike (reimplement PRNG + FNV + one noise value,
assert the golden vectors) is the recommended way to validate a new port.

## Architecture (shared model)

Two abstract concepts, each with three per-dimension interfaces:

- `NoiseGenerator` (+ `NoiseGenerator{1,2,3}D`) — generate a single octave.
- `FractalNoiseGenerator` (+ `FractalNoiseGenerator{1,2,3}D`) — stack octaves
  (fBm). **Fractal is a technique, not an algorithm**: the octave-stacking engine
  is generic/internal; only per-algorithm classes (`FractalPerlinNoise{D}`) are
  concrete.

Each algorithm exposes, per dimension, a **class** (reuse) and a one-shot
**function**, in single-octave and fractal flavours (e.g. `PerlinNoise2D` /
`perlin2D`, `FractalPerlinNoise2D` / `fractalPerlin2D`). Region sampling
(`sampleLine`/`Grid`/`Volume` + per-algo one-shots) turns any generator into a
curve/image/volume. `toUnitRange` remaps `[-1, 1]` → `[0, 1]`.

Conventions: seed is `number | string` (default `0`); output is `[-1, 1]`; the API
is idiomatic per language (TS options object, Python keyword-only) but the **names
are homogeneous** (only casing differs).

Adding a new algorithm → follow the same 4-entry-per-dimension shape, keep names
homogeneous across packages, and add conformance vectors.

## Releasing

- **Independent cycles per package.** Trigger = package-scoped git tags:
  `typescript-v1.2.3`, `python-v1.0.0` (`-rc`/`rc` suffix → pre-release channel).
- CI (`.github/workflows/release.yml`) does install → test → build → **set version
  from the tag** → publish (npm + GitHub Packages; PyPI via OIDC trusted
  publishing). `snapshot.yml` publishes dev pre-releases on every push to `main`.
- Prerequisites: `NPM_TOKEN` secret; a PyPI trusted publisher (pending publisher
  for the first release).

## Docs map

- Users: root `README.md` + `packages/<lang>/README.md`.
- How Perlin works & is implemented (1D→ND, hashing, fade, fBm, normalization,
  cross-language notes): `docs/PERLIN_NOISE.md`.
- Contributing / commit conventions: `CONTRIBUTING.md`.
- `API_CHANGE.md` (untracked, local): analysis of API-stability motifs that were
  hardened before 1.0.0 — historical rationale, not part of the release.
