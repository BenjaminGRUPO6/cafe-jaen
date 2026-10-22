import { beforeEach, describe, expect, it } from "vitest";
import type { LivePrice } from "../../shared/api/types";
import { loadLastPrice, saveLastPrice } from "./lastPriceCache";

const PRICE: LivePrice = {
  quoted_at: "2026-11-04T08:55:00-05:00",
  date: "2026-11-04",
  cents_per_pound: 300,
  price_soles: 1140.89,
  previous_close_soles: 1100,
  change_soles: 40.89,
  change_pct: 3.72,
  unit: "S/ por quintal (46 kg)",
  market: "Bolsa de Nueva York (ICE), café arábica",
  market_open: true,
  stale: false,
  sources: ["Yahoo Finance", "Stooq", "BCRP"],
  local_estimates: [],
};

describe("caché del último precio (PA-09-2)", () => {
  beforeEach(() => localStorage.clear());

  it("devuelve null si nunca se guardó un precio", () => {
    expect(loadLastPrice()).toBeNull();
  });

  it("recupera el último precio con la hora en que se guardó", () => {
    saveLastPrice(PRICE, new Date("2026-11-04T14:05:00Z"));

    expect(loadLastPrice()).toEqual({ price: PRICE, savedAt: "2026-11-04T14:05:00.000Z" });
  });
});
