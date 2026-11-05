import { describe, expect, it } from "vitest";
import { preview } from "./support";

describe("atención", () => {
  it("resume los mensajes largos en una línea", () => {
    expect(preview("Hola\n  ¿cada cuánto   cambia?")).toBe("Hola ¿cada cuánto cambia?");
    expect(preview("x".repeat(100), 10)).toBe("xxxxxxxxx…");
  });
});
