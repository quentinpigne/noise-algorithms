# noise-algorithms

A collection of **noise generation algorithms** implemented in several
languages, each published as an idiomatic, standalone library on its language's
package registry.

The goal is to provide clean, tested and documented implementations of the same
algorithms (Perlin, and more to come) that can be used as external dependencies
in real projects.

## Packages

| Language | Package | Registry | Source |
| --- | --- | --- | --- |
| TypeScript | [`@quentinpigne/noise-algorithms`](https://www.npmjs.com/package/@quentinpigne/noise-algorithms) | npm / GitHub Packages | [`packages/typescript`](./packages/typescript) |
| Python | [`noise-algorithms`](https://pypi.org/project/noise-algorithms/) | PyPI | [`packages/python`](./packages/python) |

## Algorithms

| Algorithm | 1D | 2D | 3D |
| --- | :-: | :-: | :-: |
| [Perlin noise](https://en.wikipedia.org/wiki/Perlin_noise) | ✅ | ✅ | ✅ |

Each implementation supports fractal (multi-octave) noise configured with
`seed`, `scale`, `octaves`, `lacunarity` and `persistence`, and returns values
in the `[-1, 1]` interval.

For a detailed explanation of how Perlin noise works (1D → N-D) and how it is
implemented here, see [`docs/PERLIN_NOISE.md`](./docs/PERLIN_NOISE.md).

## Quick start

**TypeScript**

```sh
npm install @quentinpigne/noise-algorithms
```

```ts
import { PerlinNoise2D } from "@quentinpigne/noise-algorithms/perlin-noise";

const perlin = new PerlinNoise2D(42);
console.log(perlin.noise(12, 7)); // value in [-1, 1]
```

**Python**

```sh
pip install noise-algorithms
```

```python
from noise_algorithms import PerlinNoise2D

print(PerlinNoise2D(seed=42).noise(12, 7))  # value in [-1, 1]
```

See each package's README for the full API and configuration options.

## Repository layout

```
packages/
  typescript/   # @quentinpigne/noise-algorithms (npm / GitHub Packages)
  python/       # noise-algorithms (PyPI)
```

## Roadmap

An **indicative** roadmap — possible directions, not firm commitments or a
schedule. Order is not significant, and suggestions are welcome.

**Noise algorithms**

- [x] Perlin noise (1D / 2D / 3D)
- [ ] Simplex / OpenSimplex noise
- [ ] Value noise
- [ ] Worley (cellular) noise
- [ ] 4D Perlin noise (e.g. for looping animations)

**Languages**

- [x] TypeScript — npm / GitHub Packages
- [x] Python — PyPI
- [ ] Rust — crates.io
- [ ] Go — pkg.go.dev
- [ ] C / C++

**Cross-cutting features**

- [ ] Seamless / tileable noise
- [ ] Domain warping
- [ ] Analytic derivatives (gradients)
- [ ] Consistent output across languages for a given seed

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE) © Quentin Pigné
