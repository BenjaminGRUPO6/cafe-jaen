import { beforeEach, describe, expect, it } from "vitest";
import { readSession, writeSession } from "./storage";

const KEY = "cafe-jaen.token";

describe("sesión por pestaña", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it("una pestaña nueva entra con la última sesión recordada", () => {
    localStorage.setItem(KEY, "caficultor");
    expect(readSession(KEY)).toBe("caficultor");
  });

  it("ingresar con otra cuenta en otra pestaña no cambia la de esta pestaña", () => {
    writeSession(KEY, "caficultor");
    localStorage.setItem(KEY, "administrador"); // otra pestaña ingresó como equipo
    expect(readSession(KEY)).toBe("caficultor");
  });

  it("al salir se olvida la sesión recordada solo si era la de esta pestaña", () => {
    writeSession(KEY, "caficultor");
    localStorage.setItem(KEY, "administrador");
    writeSession(KEY, null);
    expect(localStorage.getItem(KEY)).toBe("administrador");
    expect(sessionStorage.getItem(KEY)).toBeNull();
  });
});
