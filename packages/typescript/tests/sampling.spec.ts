import { sampleLine, sampleGrid, sampleVolume } from "../src/sampling";
import {
  PerlinNoise1D,
  PerlinNoise2D,
  PerlinNoise3D,
  FractalPerlinNoise2D,
  perlinLine,
  perlinGrid,
  perlinVolume,
  fractalPerlinGrid,
} from "../src/perlin-noise";

describe("sampleLine", () => {
  it("returns `count` values matching noise() at each coordinate", () => {
    const gen = new PerlinNoise1D({ seed: 42 });
    const line = sampleLine(gen, { count: 5, start: 2, step: 0.5 });
    expect(line).toHaveLength(5);
    line.forEach((value, i) => {
      expect(value).toBe(gen.noise(2 + i * 0.5));
    });
  });

  it("defaults start to 0 and step to 1", () => {
    const gen = new PerlinNoise1D({ seed: 7 });
    const line = sampleLine(gen, { count: 3 });
    expect(line).toEqual([gen.noise(0), gen.noise(1), gen.noise(2)]);
  });
});

describe("sampleGrid", () => {
  it("returns a height×width grid indexed as grid[y][x]", () => {
    const gen = new FractalPerlinNoise2D({ seed: 42, frequency: 0.05 });
    const grid = sampleGrid(gen, { width: 3, height: 2 });
    expect(grid).toHaveLength(2); // rows
    expect(grid[0]).toHaveLength(3); // columns
    for (let y = 0; y < 2; y++) {
      for (let x = 0; x < 3; x++) {
        expect(grid[y][x]).toBe(gen.noise(x, y));
      }
    }
  });

  it("honours origin and step", () => {
    const gen = new PerlinNoise2D({ seed: 1 });
    const grid = sampleGrid(gen, {
      width: 2,
      height: 2,
      startX: 10,
      startY: 20,
      step: 0.25,
    });
    expect(grid[1][0]).toBe(gen.noise(10, 20.25));
    expect(grid[0][1]).toBe(gen.noise(10.25, 20));
  });
});

describe("sampleVolume", () => {
  it("returns a depth×height×width volume indexed as volume[z][y][x]", () => {
    const gen = new PerlinNoise3D({ seed: 42 });
    const volume = sampleVolume(gen, { width: 2, height: 3, depth: 4 });
    expect(volume).toHaveLength(4); // depth
    expect(volume[0]).toHaveLength(3); // height
    expect(volume[0][0]).toHaveLength(2); // width
    expect(volume[3][2][1]).toBe(gen.noise(1, 2, 3));
  });
});

describe("region one-shots match building a generator and sampling it", () => {
  it("perlinLine == sampleLine(new PerlinNoise1D)", () => {
    expect(perlinLine({ seed: 7, count: 4, step: 0.5 })).toEqual(
      sampleLine(new PerlinNoise1D({ seed: 7 }), { count: 4, step: 0.5 }),
    );
  });

  it("perlinGrid == sampleGrid(new PerlinNoise2D)", () => {
    expect(perlinGrid({ seed: 1, width: 3, height: 2 })).toEqual(
      sampleGrid(new PerlinNoise2D({ seed: 1 }), { width: 3, height: 2 }),
    );
  });

  it("perlinVolume == sampleVolume(new PerlinNoise3D)", () => {
    expect(perlinVolume({ seed: 2, width: 2, height: 2, depth: 2 })).toEqual(
      sampleVolume(new PerlinNoise3D({ seed: 2 }), {
        width: 2,
        height: 2,
        depth: 2,
      }),
    );
  });

  it("fractalPerlinGrid == sampleGrid(new FractalPerlinNoise2D)", () => {
    expect(
      fractalPerlinGrid({ seed: 42, frequency: 0.05, width: 4, height: 4 }),
    ).toEqual(
      sampleGrid(new FractalPerlinNoise2D({ seed: 42, frequency: 0.05 }), {
        width: 4,
        height: 4,
      }),
    );
  });
});
