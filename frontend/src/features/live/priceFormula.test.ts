import { describe, expect, it } from "vitest";
import { POUNDS_PER_QUINTAL, priceSteps } from "./priceFormula";

describe("fórmula del precio", () => {
  it("convierte ¢/lb a dólares por quintal de 46 kg", () => {
    const steps = priceSteps(300);
    expect(POUNDS_PER_QUINTAL).toBeCloseTo(101.41, 2);
    expect(steps.usdPerPound).toBe(3);
    // 3 US$/lb × 101,41 lb × S/ 3,75 = S/ 1140,89 (igual que el backend)
    expect(steps.usdPerQuintal * 3.75).toBeCloseTo(1140.89, 2);
  });
});
