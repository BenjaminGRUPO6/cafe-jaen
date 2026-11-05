import { describe, expect, it } from "vitest";
import { localTrend } from "./LocalEstimateCard";

describe("línea de hoy en Jaén", () => {
  it("aplica el porcentaje de las cooperativas a la bolsa de cada minuto", () => {
    expect(localTrend([1000, 1010, Number.NaN], 70)).toEqual([700, 707]);
  });
});
