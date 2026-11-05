import { describe, expect, it } from "vitest";
import { quoteSourceLinks, quoteSourceUrl } from "./sources";

describe("fuentes", () => {
  it("muestra primero las webs que respaldaron el precio y luego las demás", () => {
    const links = quoteSourceLinks(["Stooq"]);
    expect(links.map((l) => l.name)).toEqual(["Stooq", "Yahoo Finance", "CNBC", "TradingView"]);
    // Sin respaldar el precio, Stooq no se lista (exige clave desde 2026)
    expect(quoteSourceLinks(["CNBC"]).map((l) => l.name)).toEqual([
      "CNBC",
      "Yahoo Finance",
      "TradingView",
    ]);
    expect(links.every((l) => l.url.startsWith("https://"))).toBe(true);
  });

  it("ignora nombres que no son webs conocidas", () => {
    expect(quoteSourceLinks(["Otra"]).map((l) => l.name)).toEqual([
      "Yahoo Finance",
      "CNBC",
      "TradingView",
    ]);
  });

  it("da el enlace de cada web por el nombre que guarda la API", () => {
    expect(quoteSourceUrl("CNBC")).toBe("https://www.cnbc.com/quotes/@KC.1");
    expect(quoteSourceUrl("Otra")).toBeUndefined();
  });
});
