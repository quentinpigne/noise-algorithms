import { PNG } from "pngjs";
import { PerlinNoise1D } from "../src/perlin-noise/perlin-noise-1d";
import { PerlinNoise2D } from "../src/perlin-noise/perlin-noise-2d";
import { PerlinNoise3D } from "../src/perlin-noise/perlin-noise-3d";
import fs from "fs";
import path from "path";

export interface PerlinNoiseImageOptions {
  width?: number;
  height?: number;
  seed?: number;
  scale?: number;
  octaves?: number;
  lacunarity?: number;
  persistence?: number;
  outputPath?: string;
}

export class PerlinNoiseImage {
  private static DEFAULT_OPTIONS: PerlinNoiseImageOptions = {
    width: 512,
    height: 512,
    seed: 42,
    scale: 0.01,
    octaves: 4,
    lacunarity: 2,
    persistence: 0.5,
    outputPath: "perlin-noise.png"
  };

  /**
   * Generate a 1D Perlin noise image as PNG
   * @param options Perlin noise options
   * @returns PNG buffer
   */
  static generate1D(options: PerlinNoiseImageOptions = {}): Buffer {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    const png = new PNG({
      width: opts.width!,
      height: opts.height!,
      colorType: 0, // Grayscale
      inputColorType: 0
    });

    const noise = new PerlinNoise1D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence
    );

    for (let x = 0; x < opts.width!; x++) {
      const noiseValue = noise.noise(x);
      const normalizedValue = (noiseValue + 1) / 2; // Convert from [-1, 1] to [0, 1]
      const pixelValue = Math.floor(normalizedValue * 255);

      for (let y = 0; y < opts.height!; y++) {
        const idx = (png.width * y + x) << 0;
        png.data[idx] = pixelValue; // Grayscale value
      }
    }

    return PNG.sync.write(png);
  }

  /**
   * Generate a 2D Perlin noise image as PNG
   * @param options Perlin noise options
   * @returns PNG buffer
   */
  static generate2D(options: PerlinNoiseImageOptions = {}): Buffer {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    const png = new PNG({
      width: opts.width!,
      height: opts.height!,
      colorType: 0, // Grayscale
      inputColorType: 0
    });

    const noise = new PerlinNoise2D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence
    );

    for (let y = 0; y < opts.height!; y++) {
      for (let x = 0; x < opts.width!; x++) {
        const noiseValue = noise.noise(x, y);
        const normalizedValue = (noiseValue + 1) / 2; // Convert from [-1, 1] to [0, 1]
        const pixelValue = Math.floor(normalizedValue * 255);

        const idx = (png.width * y + x) << 0;
        png.data[idx] = pixelValue; // Grayscale value
      }
    }

    return PNG.sync.write(png);
  }

  /**
   * Generate a 3D Perlin noise image (2D slice) as PNG
   * @param options Perlin noise options
   * @param zSlice Z coordinate for the 2D slice
   * @returns PNG buffer
   */
  static generate3D(options: PerlinNoiseImageOptions = {}, zSlice: number = 0): Buffer {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    const png = new PNG({
      width: opts.width!,
      height: opts.height!,
      colorType: 0, // Grayscale
      inputColorType: 0
    });

    const noise = new PerlinNoise3D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence
    );

    for (let y = 0; y < opts.height!; y++) {
      for (let x = 0; x < opts.width!; x++) {
        const noiseValue = noise.noise(x, y, zSlice);
        const normalizedValue = (noiseValue + 1) / 2; // Convert from [-1, 1] to [0, 1]
        const pixelValue = Math.floor(normalizedValue * 255);

        const idx = (png.width * y + x) << 0;
        png.data[idx] = pixelValue; // Grayscale value
      }
    }

    return PNG.sync.write(png);
  }

  /**
   * Save PNG buffer to file
   * @param pngBuffer PNG buffer to save
   * @param outputPath Output file path
   */
  static savePNG(pngBuffer: Buffer, outputPath: string): void {
    fs.writeFileSync(outputPath, pngBuffer);
    console.log(`Image saved to ${outputPath}`);
  }

  /**
   * Generate and save Perlin noise images for all dimensions
   * @param options Perlin noise options
   * @param outputDir Output directory
   */
  static generateAllDimensions(options: PerlinNoiseImageOptions = {}, outputDir: string = "./"): void {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Generate 1D noise image
    const png1D = this.generate1D(opts);
    const outputPath1D = path.join(outputDir, "perlin-noise-1d.png");
    this.savePNG(png1D, outputPath1D);

    // Generate 2D noise image
    const png2D = this.generate2D(opts);
    const outputPath2D = path.join(outputDir, "perlin-noise-2d.png");
    this.savePNG(png2D, outputPath2D);

    // Generate 3D noise image (2D slice)
    const png3D = this.generate3D(opts);
    const outputPath3D = path.join(outputDir, "perlin-noise-3d.png");
    this.savePNG(png3D, outputPath3D);

    console.log("All Perlin noise images generated successfully!");
  }
}
