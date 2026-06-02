#!/usr/bin/env tsx

import { PerlinNoiseImage } from "./perlin-noise-image.ts";
import path from "path";
import fs from "fs";

// Parse command line arguments
const args = process.argv.slice(2);
let outputDir = "./images";
let width = 512;
let height = 512;
let seed = 42;
let scale = 0.01;
let octaves = 4;
let lacunarity = 2;
let persistence = 0.5;

// Parse arguments
for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (arg === "--output" || arg === "-o") {
    outputDir = args[++i];
  } else if (arg === "--width" || arg === "-w") {
    width = parseInt(args[++i]);
  } else if (arg === "--height" || arg === "-h") {
    height = parseInt(args[++i]);
  } else if (arg === "--seed" || arg === "-s") {
    seed = parseInt(args[++i]);
  } else if (arg === "--scale") {
    scale = parseFloat(args[++i]);
  } else if (arg === "--octaves") {
    octaves = parseInt(args[++i]);
  } else if (arg === "--lacunarity") {
    lacunarity = parseFloat(args[++i]);
  } else if (arg === "--persistence") {
    persistence = parseFloat(args[++i]);
  }
}

console.log("Generating Perlin noise images with the following parameters:");
console.log(`- Output directory: ${outputDir}`);
console.log(`- Width: ${width}`);
console.log(`- Height: ${height}`);
console.log(`- Seed: ${seed}`);
console.log(`- Scale: ${scale}`);
console.log(`- Octaves: ${octaves}`);
console.log(`- Lacunarity: ${lacunarity}`);
console.log(`- Persistence: ${persistence}`);

// Generate images for all dimensions
PerlinNoiseImage.generateAllDimensions(
  {
    width,
    height,
    seed,
    scale,
    octaves,
    lacunarity,
    persistence
  },
  outputDir
);

console.log("\nGeneration complete!");
console.log(`Images saved to: ${path.resolve(outputDir)}`);
