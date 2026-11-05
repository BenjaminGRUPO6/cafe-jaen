import { describe, expect, it } from "vitest";
import { delayMinutes, tickDay, tickTime, timeTicks, toTimed } from "./chartAxis";

const at = (iso: string) => Date.parse(iso);

describe("eje del gráfico", () => {
  it("marca la hora cada 60 minutos, redonda, en un día completo", () => {
    const ticks = timeTicks(at("2026-11-05T06:51:00-05:00"), at("2026-11-05T10:05:00-05:00"), true);
    expect(ticks.map(tickTime)).toEqual(["07:00", "08:00", "09:00", "10:00"]);
  });

  it("marca cada 15 minutos si hay poco tiempo", () => {
    const ticks = timeTicks(at("2026-11-05T09:20:00-05:00"), at("2026-11-05T10:05:00-05:00"), true);
    expect(ticks.map(tickTime)).toEqual(["09:30", "09:45", "10:00"]);
  });

  it("en 30 días marca cada lunes, aunque falten los fines de semana", () => {
    const points = toTimed(
      [
        { date: "2026-10-06", price_soles: 1 },
        { date: "2026-11-05", price_soles: 2 },
      ],
      false,
    );
    const ticks = timeTicks(points[0].at, points[1].at, false);
    expect(ticks.map(tickDay)).toEqual(["12/10", "19/10", "26/10", "02/11"]);
  });

  it("en 90 días marca cada cuatro semanas", () => {
    const ticks = timeTicks(
      at("2026-08-07T12:00:00-05:00"),
      at("2026-11-05T12:00:00-05:00"),
      false,
    );
    expect(ticks.map(tickDay)).toEqual(["10/08", "07/09", "05/10", "02/11"]);
  });

  it("calcula el retraso de la última cotización", () => {
    expect(delayMinutes(at("2026-11-05T10:05:00-05:00"), at("2026-11-05T10:15:30-05:00"))).toBe(11);
  });
});
