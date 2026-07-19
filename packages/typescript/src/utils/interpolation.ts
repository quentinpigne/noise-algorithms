/** Perlin's smoothing function `6t^5 - 15t^4 + 10t^3` (quintic smootherstep). */
export function fade(t: number): number {
  return t * t * t * (t * (t * 6 - 15) + 10);
}

/** Linear interpolation */
export function lerp(a: number, b: number, t: number): number {
  return a + t * (b - a);
}
