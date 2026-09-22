# CLAUDE.md — Python package

`noise-algorithms` — pure Python (no runtime deps), typed (`py.typed`), Python ≥
3.10, hatchling build. Read the root `CLAUDE.md` first for the cross-language
invariant and architecture.

## Commands (run from `packages/python`, uses [uv](https://docs.astral.sh/uv/))

```sh
uv sync                 # install dev deps
uv run pytest           # unit + integration tests
uv run ruff check .     # lint
uv run ruff format .    # format
uv build                # sdist + wheel
```

Coverage (ephemeral): `uv run --with pytest-cov pytest -m "not integration" --cov=noise_algorithms`.

## Layout

- `noise_generator.py`, `fractal_noise_generator.py` — the two abstract concept
  base classes.
- `interfaces.py` — `NoiseGenerator{1,2,3}D` + `FractalNoiseGenerator{1,2,3}D`
  runtime-checkable Protocols (the "interfaces").
- `perlin/` — `_base.py` (abstract engine, `_octave`, `_scaled`,
  `_NORMALIZATION` per subclass), `perlin_{1,2,3}d.py` (classes + `perlin_{d}` +
  `FractalPerlinNoise{D}` + `fractal_perlin_{d}` + region one-shots; each
  **unrolls its own octave and stacking loop** and is pinned to the generic
  engine by `tests/test_octave_agreement.py` — see the root `CLAUDE.md`).
- `sampling.py` — `sample_line`/`sample_grid`/`sample_volume`.
- `output_range.py` — `to_unit_range`.
- `_seeded_random.py` (`xorshift32`, `fnv1a32`), `_permutation.py`,
  `_interpolation.py` (`fade`, `lerp`) — **private** (underscore-prefixed).

## Conventions & gotchas

- Parameters are **keyword-only** (`*,`); seed accepts `int | str` (string hashed
  via `fnv1a32`). Python is UTF-8 native, so `fnv1a32` iterates `text.encode()` /
  `str.bytes` directly.
- `NoiseGenerator(ABC)` has no abstract method (`noise` is dimension-specific, on
  the Protocols) → it carries a `# noqa: B024`. Keep it.
- **Three version sources**: `pyproject.toml`, `__init__.py:__version__`, and the
  `noise-algorithms` entry in `uv.lock`. Release CI sets only the pyproject
  version, from the tag; bump the other two by hand — `__version__` by editing it,
  the lock by running `uv lock`. Nothing runs `uv sync --locked`, so a stale lock
  fails no build: it just sits wrong in the repo and dirties the tree on the next
  `uv sync`.
- Integration tests build a wheel and render images in an isolated subprocess,
  comparing to `tests/snapshots/`. Refresh with `UPDATE_SNAPSHOTS=1 uv run pytest`.
- `_gradient` and `_sample` on the concrete dimensions **feed `_octave` /
  `_fractal` only**; `noise` inlines them. Overriding either on `PerlinNoise3D`
  or `FractalPerlinNoise3D` is silently ignored — derive the abstract
  `PerlinNoise` / `FractalNoiseGenerator` instead.
- Any change to the noise math must stay bit-identical with TypeScript — see root
  `CLAUDE.md`, update the shared golden vectors in `tests/test_perlin.py`, and
  keep `tests/test_octave_agreement.py` green.
- The conformance vectors assert with `==`, never `pytest.approx`: the invariant
  is bit-for-bit, and a tolerance cannot express it. Each literal is the shortest
  decimal that round-trips to its f64 and parses identically in both languages —
  its hex bits are in the comment beside it. Regenerate with `repr()`.
