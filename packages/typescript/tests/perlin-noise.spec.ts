import { PerlinNoise1D } from "../src/perlin-noise/perlin-noise-1d";
import { PerlinNoise2D } from "../src/perlin-noise/perlin-noise-2d";
import { PerlinNoise3D } from "../src/perlin-noise/perlin-noise-3d";

describe("Perlin noise generator", () => {
  it("should generate 1D Perlin noise", () => {
    const perlin = new PerlinNoise1D(42);
    const result = perlin.noise(0.5);
    expect(result).toBeCloseTo(0.010717, 6);
  });

  it("should generate 2D Perlin noise", () => {
    const perlin = new PerlinNoise2D(42);
    const result = perlin.noise(0.5, 0.5);
    expect(result).toBeCloseTo(-0.01513, 6);
  });

  it("should generate 3D Perlin noise", () => {
    const perlin = new PerlinNoise3D(42);
    const result = perlin.noise(0.5, 0.5, 0.5);
    expect(result).toBeCloseTo(-0.015006, 6);
  });
});
