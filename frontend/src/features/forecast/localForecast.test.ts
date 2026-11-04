import { describe, expect, it } from "vitest";
import type { LocalEstimate } from "../../shared/api/types";
import { toLocalForecast } from "./localForecast";

const point = { date: "2026-11-05", expected_soles: 1500, lower_soles: 1470, upper_soles: 1530 };
const conventional: LocalEstimate = {
  coffee_type: "convencional",
  estimated_soles: 1080,
  ratio_pct: 72,
  observations: 3,
  first_day: "2026-11-01",
  last_day: "2026-11-03",
  few_data: false,
};

describe("toLocalForecast", () => {
  it("aplica el porcentaje de las cooperativas al pronóstico de la bolsa", () => {
    expect(toLocalForecast([point], conventional)[0].local_soles).toBe(1080);
  });

  it("redondea a céntimos", () => {
    const [result] = toLocalForecast([{ ...point, expected_soles: 1509.6 }], conventional);
    expect(result.local_soles).toBe(1086.91);
  });

  it("sin precios de cooperativas solo deja el pronóstico de la bolsa", () => {
    expect(toLocalForecast([point], undefined)[0].local_soles).toBeNull();
  });
});
