import { describe, expect, it } from "vitest";
import {
  formatCents,
  formatDate,
  formatDateTime,
  formatPercent,
  formatSoles,
  formatTime,
} from "./format";

describe("formato peruano", () => {
  it("usa coma decimal en soles", () => {
    expect(formatSoles(1140.89)).toBe("S/ 1140,89");
  });

  it("redondea porcentajes a un decimal", () => {
    expect(formatPercent(3.72)).toBe("3,7 %");
  });

  it("muestra fechas como dd/mm/aaaa", () => {
    expect(formatDate("2026-11-04")).toBe("04/11/2026");
  });

  it("muestra fecha y hora corta", () => {
    expect(formatDateTime(new Date(2026, 10, 4, 9, 5))).toBe("04/11 09:05");
  });

  it("toma la hora de Lima tal como la envía la API", () => {
    expect(formatTime("2026-11-04T08:55:00-05:00")).toBe("08:55");
  });

  it("muestra la cotización de la bolsa en centavos por libra", () => {
    expect(formatCents(300.5)).toBe("300,50 ¢/lb");
  });
});
