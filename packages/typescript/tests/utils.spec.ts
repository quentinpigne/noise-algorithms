import { fade, lerp } from "../src/utils/interpolation";
import { utf8Bytes } from "../src/utils/utf8";

describe("interpolation", () => {
  describe("fade", () => {
    it("maps the boundaries and the midpoint to themselves", () => {
      expect(fade(0)).toBe(0);
      expect(fade(1)).toBe(1);
      expect(fade(0.5)).toBeCloseTo(0.5, 10);
    });

    it("is monotonically increasing on [0, 1]", () => {
      let previous = fade(0);
      for (let i = 1; i <= 10; i++) {
        const current = fade(i / 10);
        expect(current).toBeGreaterThanOrEqual(previous);
        previous = current;
      }
    });
  });

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
});

describe("utf8Bytes", () => {
  it("encodes ASCII as one byte per character", () => {
    expect(utf8Bytes("hello")).toEqual([104, 101, 108, 108, 111]);
  });

  it("encodes multi-byte code points like str.encode('utf-8')", () => {
    expect(utf8Bytes("é")).toEqual([0xc3, 0xa9]); // 2 bytes
    expect(utf8Bytes("€")).toEqual([0xe2, 0x82, 0xac]); // 3 bytes
    expect(utf8Bytes("😀")).toEqual([0xf0, 0x9f, 0x98, 0x80]); // 4 bytes (surrogate pair)
  });
});
