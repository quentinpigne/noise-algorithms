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
from noise_algorithms import PerlinConfig, perlin_2d

print(perlin_2d(12, 7, PerlinConfig(seed=42)))  # value in [-1, 1]
```

See each package's README for the full API and configuration options.

## Repository layout

```
packages/
  typescript/   # @quentinpigne/noise-algorithms (npm / GitHub Packages)
  python/       # noise-algorithms (PyPI)
```

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE) © Quentin Pigné
