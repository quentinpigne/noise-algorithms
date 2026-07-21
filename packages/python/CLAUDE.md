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
- `perlin/` — `_base.py` (abstract engine, `_octave`, `_NORMALIZATION` per
  subclass), `perlin_{1,2,3}d.py` (classes + `perlin_{d}` + `FractalPerlinNoise{D}`
  + `fractal_perlin_{d}` + region one-shots).
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
- **Two version sources**: `pyproject.toml` and `__init__.py:__version__`. The
  release CI sets the pyproject version from the tag but NOT `__version__` — bump
  `__version__` manually to match.
- Integration tests build a wheel and render images in an isolated subprocess,
  comparing to `tests/snapshots/`. Refresh with `UPDATE_SNAPSHOTS=1 uv run pytest`.
- Any change to the noise math must stay bit-identical with TypeScript — see root
  `CLAUDE.md`, update the shared golden vectors in `tests/test_perlin.py`.
