import { describe, expect, it } from "vitest";
import type { LocalPriceObservation } from "../../shared/api/types";
import { latestByCooperative } from "./latestByCooperative";

const item = (
  id: number,
  cooperative: string,
  observed_at: string,
  coffee_type: LocalPriceObservation["coffee_type"] = "convencional",
): LocalPriceObservation => ({
  id,
  cooperative,
  observed_at,
  coffee_type,
  paid_soles: 1000 + id,
  exchange_soles: 1500,
  ratio_pct: 70,
});

describe("precio por cooperativa", () => {
  it("deja solo el último precio de cada cooperativa para el tipo elegido", () => {
    const result = latestByCooperative(
      [
        item(1, "A", "2026-11-01T09:00:00-05:00"),
        item(2, "A", "2026-11-04T09:00:00-05:00"),
        item(3, "B", "2026-11-03T09:00:00-05:00"),
        item(4, "B", "2026-11-05T09:00:00-05:00", "organico"),
      ],
      "convencional",
    );
    expect(result.map((o) => o.id)).toEqual([2, 3]);
  });
});
