import { describe, expect, it } from "vitest";
import { isDemoSource, quoteSourceLinks } from "./sources";

describe("fuentes", () => {
  it("enlaza solo las webs conocidas", () => {
    const links = quoteSourceLinks(["Yahoo Finance", "Stooq", "Otra"]);
    expect(links.map((l) => l.name)).toEqual(["Yahoo Finance", "Stooq"]);
    expect(links.every((l) => l.url.startsWith("https://"))).toBe(true);
  });

  it("con el precio de demostración muestra las webs que se consultan con datos reales", () => {
    const links = quoteSourceLinks(["DEMO (sintético)"]);
    expect(links.map((l) => l.name)).toEqual(["Yahoo Finance", "Stooq"]);
  });

  it("reconoce el precio de demostración", () => {
    expect(isDemoSource(["DEMO (sintético)"])).toBe(true);
    expect(isDemoSource(["Stooq"])).toBe(false);
  });
});
