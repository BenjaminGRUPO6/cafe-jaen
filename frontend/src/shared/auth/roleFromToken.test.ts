import { describe, expect, it } from "vitest";
import { roleFromToken } from "./AuthContext";

const token = (payload: object) => `x.${btoa(JSON.stringify(payload))}.firma`;

describe("rol en el token (HU12)", () => {
  it("reconoce al administrador del equipo", () => {
    expect(roleFromToken(token({ sub: "1", role: "admin" }))).toBe("admin");
  });

  it("devuelve null si no hay token o no se puede leer", () => {
    expect(roleFromToken(null)).toBeNull();
    expect(roleFromToken("basura")).toBeNull();
  });
});
