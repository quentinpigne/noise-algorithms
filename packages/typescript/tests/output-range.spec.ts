import { toUnitRange } from "../src/output-range";

describe("toUnitRange", () => {
  it("maps the signed range [-1, 1] onto the unit range [0, 1]", () => {
    expect(toUnitRange(-1)).toBe(0);
    expect(toUnitRange(0)).toBe(0.5);
    expect(toUnitRange(1)).toBe(1);
  });
});
