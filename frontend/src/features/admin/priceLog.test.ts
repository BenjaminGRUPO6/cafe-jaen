import { describe, expect, it } from "vitest";
import { summarizeDay, todayInput, type PriceLogEntry } from "./priceLog";

const entry = (published: boolean, statuses: string[]): PriceLogEntry => ({
  quoted_at: "2026-11-05T10:00:00-05:00",
  published,
  cents_per_pound: published ? 300 : null,
  median_cents: 300,
  exchange_rate: 3.75,
  price_soles: published ? 1140 : null,
  sources: [],
  local_soles: {},
  readings: statuses.map((status) => ({
    source: status,
    status: status as PriceLogEntry["readings"][number]["status"],
    cents_per_pound: 300,
    quoted_at: null,
    deviation_pct: 0,
    detail: null,
  })),
});

describe("historial de la bolsa", () => {
  it("resume las consultas del día", () => {
    const summary = summarizeDay([
      entry(true, ["usada", "usada", "descartada"]),
      entry(true, ["usada", "sin respuesta"]),
      entry(false, ["descartada", "descartada"]),
    ]);
    expect(summary).toEqual({ collections: 3, published: 2, withDiscarded: 2, withFailures: 1 });
  });

  it("da la fecha de hoy para el campo de fecha", () => {
    expect(todayInput(new Date(2026, 10, 5, 9, 30))).toBe("2026-11-05");
  });
});
