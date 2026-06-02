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
    outputPath: "perlin-noise.png",
  };

  /** Map a noise value in [-1, 1] to a grayscale byte in [0, 255]. */
  private static toGray(noiseValue: number): number {
    const normalized = (noiseValue + 1) / 2;
    return Math.max(0, Math.min(255, Math.floor(normalized * 255)));
  }

  /** Write a grayscale value as an opaque RGBA pixel. */
  private static setPixel(png: PNG, x: number, y: number, gray: number): void {
    const idx = (png.width * y + x) << 2;
    png.data[idx] = gray;
    png.data[idx + 1] = gray;
    png.data[idx + 2] = gray;
    png.data[idx + 3] = 255;
  }

  /**
   * Generate a 1D Perlin noise image as PNG
   * @param options Perlin noise options
   * @returns PNG buffer
   */
  static generate1D(options: PerlinNoiseImageOptions = {}): Buffer {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    const png = new PNG({ width: opts.width!, height: opts.height! });

    const noise = new PerlinNoise1D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence,
    );

    for (let x = 0; x < opts.width!; x++) {
      const gray = PerlinNoiseImage.toGray(noise.noise(x));

      for (let y = 0; y < opts.height!; y++) {
        PerlinNoiseImage.setPixel(png, x, y, gray);
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

    const png = new PNG({ width: opts.width!, height: opts.height! });

    const noise = new PerlinNoise2D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence,
    );

    for (let y = 0; y < opts.height!; y++) {
      for (let x = 0; x < opts.width!; x++) {
        PerlinNoiseImage.setPixel(
          png,
          x,
          y,
          PerlinNoiseImage.toGray(noise.noise(x, y)),
        );
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
  static generate3D(
    options: PerlinNoiseImageOptions = {},
    zSlice: number = 0,
  ): Buffer {
    const opts = { ...this.DEFAULT_OPTIONS, ...options };

    const png = new PNG({ width: opts.width!, height: opts.height! });

    const noise = new PerlinNoise3D(
      opts.seed,
      opts.scale,
      opts.octaves,
      opts.lacunarity,
      opts.persistence,
    );

    for (let y = 0; y < opts.height!; y++) {
      for (let x = 0; x < opts.width!; x++) {
        PerlinNoiseImage.setPixel(
          png,
          x,
          y,
          PerlinNoiseImage.toGray(noise.noise(x, y, zSlice)),
        );
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
  static generateAllDimensions(
    options: PerlinNoiseImageOptions = {},
    outputDir: string = "./",
  ): void {
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
