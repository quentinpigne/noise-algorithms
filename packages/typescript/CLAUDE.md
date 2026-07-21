# CLAUDE.md — TypeScript package

`@quentinpigne/noise-algorithms` — ESM library with type declarations, Node ≥ 18.
Read the root `CLAUDE.md` first for the cross-language invariant and architecture.

## Commands (run from `packages/typescript`)

```sh
npm install
npm test                  # Vitest unit tests
npm run build             # tsdown → dist/ (.mjs + .d.mts)
npm run test:integration  # build, then render images from dist/ and snapshot them
npm run lint              # ESLint
npm run format            # Prettier (write); format:check in CI
```

## Layout

- `src/noise-generator.ts`, `src/fractal-noise-generator.ts` — the two abstract
  concept classes (+ their options interfaces).
- `src/interfaces/` — dimension interfaces (type-only): `NoiseGenerator{1,2,3}D`,
  `FractalNoiseGenerator{1,2,3}D`.
- `src/perlin-noise/` — Perlin: `perlin-noise.ts` (abstract engine, `octave`),
  `perlin-noise-{1,2,3}d.ts` (classes + `perlin{D}` fns),
  `fractal-perlin-noise-{1,2,3}d.ts` (classes + `fractalPerlin{D}` + region
  one-shots). The per-dim `normalization` constant lives on each subclass.
- `src/sampling/` — `sampleLine`/`sampleGrid`/`sampleVolume` (generic).
- `src/output-range.ts` — `toUnitRange`.
- `src/utils/` — **internal, never exported**: `seeded-random.ts` (`xorshift32`,
  `fnv1a32`), `utf8.ts`, `interpolation.ts` (`fade`, `lerp`), `constants.ts`.

Entry points: `.` (abstractions, interfaces, sampling, `toUnitRange`) and
`./perlin-noise` (Perlin classes + functions). Defined in `package.json#exports`
and `tsdown.config.ts` — keep the two in sync when adding an entry point.

## Conventions & gotchas

- Constructors take a single **options object**; the seed accepts `number |
string` (string hashed via `fnv1a32`).
- `utils/` is private — nothing there is a public export. `fnv1a32` derives UTF-8
  bytes with the local `utf8Bytes` (no `TextEncoder`) so the lib needs no DOM/Node
  lib (`tsconfig` is `lib: ["es2022"]`, `types: ["vitest/globals"]`).
- `dist/` is **gitignored** and there is **no `prepublishOnly`/`prepack`** hook —
  publishing relies on CI running `npm run build` first. Don't `npm publish`
  manually without building.
- Integration tests compare against committed PNGs in `tests/snapshots/`. If output
  legitimately changes, refresh with `UPDATE_SNAPSHOTS=1 npm run test:integration`
  and eyeball the result.
- Any change to the noise math must stay bit-identical with Python — see root
  `CLAUDE.md`, update the shared golden vectors in `tests/perlin-noise.spec.ts`.
