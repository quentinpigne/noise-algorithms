import { smoothstep, lerp, coserp, cuberp } from "../src/utils/interpolation";

describe("interpolation", () => {
  describe("lerp", () => {
    it("returns the endpoints at t = 0 and t = 1", () => {
      expect(lerp(2, 8, 0)).toBe(2);
      expect(lerp(2, 8, 1)).toBe(8);
    });

    it("returns the midpoint at t = 0.5", () => {
      expect(lerp(2, 8, 0.5)).toBe(5);
    });

    it("extrapolates outside [0, 1]", () => {
      expect(lerp(0, 10, 2)).toBe(20);
      expect(lerp(0, 10, -1)).toBe(-10);
    });
  });

  describe("smoothstep", () => {
    it("clamps values outside [0, 1]", () => {
      expect(smoothstep(-0.5)).toBe(0);
      expect(smoothstep(1.5)).toBe(1);
    });

    it("maps the boundaries and the midpoint to themselves", () => {
      expect(smoothstep(0)).toBe(0);
      expect(smoothstep(1)).toBe(1);
      expect(smoothstep(0.5)).toBeCloseTo(0.5, 10);
    });

    it("is monotonically increasing on [0, 1]", () => {
      let previous = smoothstep(0);
      for (let i = 1; i <= 10; i++) {
        const current = smoothstep(i / 10);
        expect(current).toBeGreaterThanOrEqual(previous);
        previous = current;
      }
    });
  });

  describe("coserp", () => {
    it("returns the endpoints at t = 0 and t = 1", () => {
      expect(coserp(2, 8, 0)).toBeCloseTo(2, 10);
      expect(coserp(2, 8, 1)).toBeCloseTo(8, 10);
    });

    it("returns the midpoint at t = 0.5", () => {
      expect(coserp(2, 8, 0.5)).toBeCloseTo(5, 10);
    });
  });

  describe("cuberp", () => {
    it("passes through the inner control points at t = 0 and t = 1", () => {
      // cuberp(v0, v1, v2, v3, t) interpolates between v1 (t=0) and v2 (t=1).
      expect(cuberp(0, 1, 2, 3, 0)).toBeCloseTo(1, 10);
      expect(cuberp(0, 1, 2, 3, 1)).toBeCloseTo(2, 10);
    });

    it("is linear for evenly spaced collinear points", () => {
      expect(cuberp(0, 1, 2, 3, 0.5)).toBeCloseTo(1.5, 10);
    });
  });
});
