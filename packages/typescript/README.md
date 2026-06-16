# @quentinpigne/noise-algorithms

A collection of noise generation algorithms in **TypeScript**, shipped as an
ESM library with type definitions. Part of the
[noise-algorithms](https://github.com/quentinpigne/noise-algorithms) monorepo.

## Preview

Perlin noise rendered from the built library (`seed=42`, `scale=0.03`) — these
are the snapshots the integration tests verify:

|              1D (signal graph)               |                  2D (field)                  |            3D (Swiss cheese cube)            |
| :------------------------------------------: | :------------------------------------------: | :------------------------------------------: |
| ![1D](./tests/snapshots/perlin-noise-1d.png) | ![2D](./tests/snapshots/perlin-noise-2d.png) | ![3D](./tests/snapshots/perlin-noise-3d.png) |

## Installation

From npm:

```sh
npm install @quentinpigne/noise-algorithms
```

Requires Node.js ≥ 18. This package is also published to **GitHub Packages**. To install from there,
add a scoped registry to your `.npmrc`:

```
@quentinpigne:registry=https://npm.pkg.github.com
```

## Usage

The Perlin generators live under the `/perlin-noise` entry point. Each class
exposes a `noise(...)` method returning fractal (multi-octave) noise in the
`[-1, 1]` interval.

```ts
import {
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
} from "@quentinpigne/noise-algorithms/perlin-noise";

const perlin = new PerlinNoise2D(42);
const value = perlin.noise(12, 7); // [-1, 1]

new PerlinNoise1D(42).noise(3);
new PerlinNoise3D(42).noise(3, 4, 5);
```

The package root re-exports the shared abstractions and interfaces:

```ts
import {
  NoiseGenerator,
  NoiseGenerator1D,
  NoiseGenerator2D,
  NoiseGenerator3D,
} from "@quentinpigne/noise-algorithms";
```

### Constructor parameters

```ts
new PerlinNoise2D(seed?, scale?, octaves?, lacunarity?, persistence?)
```

| Parameter     | Default | Description                                             |
| ------------- | ------- | ------------------------------------------------------- |
| `seed`        | random  | Seed for the permutation table; same seed → same field. |
| `scale`       | `0.01`  | Base frequency multiplier applied to the coordinates.   |
| `octaves`     | `4`     | Number of noise layers summed together.                 |
| `lacunarity`  | `2`     | Frequency multiplier between successive octaves.        |
| `persistence` | `0.5`   | Amplitude multiplier between successive octaves.        |

## Development

```sh
npm install
npm test               # unit tests (Vitest)
npm run build          # bundle to dist/ with type declarations (tsdown)
npm run test:integration  # build, then render an image from dist/ and snapshot it
npm run lint           # ESLint
npm run format         # Prettier (write); use format:check in CI
```

Integration tests render a noise image from the built library and compare it to
the committed snapshot in `tests/snapshots/`; the rendered image is written to
`tests/output/` for inspection. Refresh the snapshot with
`UPDATE_SNAPSHOTS=1 npm run test:integration`.

A helper script under [`scripts/`](./scripts) can render the noise to PNG
images (requires [`tsx`](https://github.com/privatenumber/tsx)):

```sh
npx tsx scripts/generate-perlin-noise-images.ts --output ./images
```

## License

[MIT](./LICENSE)
