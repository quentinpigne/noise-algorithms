// Smooth function of the interval [0.0, 1.0] towards itself
export function smoothstep(w: number) {
  if (w <= 0.0) return 0.0;
  if (w >= 1.0) return 1.0;
  return w * w * (3.0 - 2.0 * w);
}

/** Linear interpolation */
export function lerp(a: number, b: number, t: number): number {
  return a + t * (b - a);
}

/** Cosine interpolation */
export function coserp(a: number, b: number, t: number): number {
  const t2 = (1 - Math.cos(t * Math.PI)) / 2;
  return a * (1 - t2) + b * t2;
}

/** Cubic interpolation */
export function cuberp(
  v0: number,
  v1: number,
  v2: number,
  v3: number,
  t: number
): number {
  const p = v3 - v2 - (v0 - v1);
  const q = v0 - v1 - p;
  const r = v2 - v0;
  const s = v1;
  return p * t ** 3 + q * t ** 2 + r * t + s;
}
