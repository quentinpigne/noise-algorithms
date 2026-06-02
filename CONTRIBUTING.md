# Contributing

Thanks for your interest in contributing to **noise-algorithms**!

This is a polyglot monorepo: each language lives under `packages/<language>`
and is an independent, independently-versioned library. Work on the package(s)
relevant to your change.

## Commit messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/),
scoped by package, e.g.:

```
feat(typescript): add value noise generator
fix(python): correct gradient indexing in 3D noise
docs: update root README
```

## TypeScript package (`packages/typescript`)

Requires Node.js ≥ 18.

```sh
cd packages/typescript
npm install
npm test          # Vitest
npm run build     # tsdown → dist/ with type declarations
```

Please make sure `npm test` and `npm run build` pass before opening a pull
request.

## Python package (`packages/python`)

Uses [uv](https://docs.astral.sh/uv/).

```sh
cd packages/python
uv sync                 # install dev dependencies
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # format
```

Please make sure tests pass and `ruff check` is clean before opening a pull
request.

## Adding a new algorithm

When adding a new noise algorithm, keep the public API consistent across
languages where possible, document it in the package README, and add tests
(including a determinism test and output-bounds checks).

### Snapshot / integration tests

Each package has an integration test that imports the **built** library, renders
a noise image and compares it to a committed snapshot in `tests/snapshots/`. The
rendered image is written to `tests/output/` (gitignored) for inspection. If a
change legitimately alters the output, refresh the snapshot with
`UPDATE_SNAPSHOTS=1` (`npm run test:integration` / `uv run pytest`) and review
the new image before committing it.

## Pull requests

- Keep changes focused; one logical change per pull request.
- Update the relevant package `CHANGELOG.md` under the `Unreleased` section.
- Update documentation when behaviour or the public API changes.
