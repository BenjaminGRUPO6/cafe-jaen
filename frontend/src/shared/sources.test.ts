import { describe, expect, it } from "vitest";
import { quoteSourceLinks } from "./sources";

describe("fuentes", () => {
  it("muestra primero las webs que respaldaron el precio y luego las demás", () => {
    const links = quoteSourceLinks(["Stooq"]);
    expect(links.map((l) => l.name)).toEqual(["Stooq", "Yahoo Finance"]);
    expect(links.every((l) => l.url.startsWith("https://"))).toBe(true);
  });

  it("ignora nombres que no son webs conocidas", () => {
    expect(quoteSourceLinks(["Otra"]).map((l) => l.name)).toEqual(["Yahoo Finance", "Stooq"]);
  });
});
