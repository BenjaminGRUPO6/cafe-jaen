import { describe, expect, it } from "vitest";
import { startOfToday, summarize, type ParticipantsReport } from "./participants";

const report: ParticipantsReport = {
  codes: { total: 10, used: 2 },
  participants: [
    {
      id: "u-911111111",
      phone: "911111111",
      email: null,
      verified: true,
      pending_code: null,
      delivered_by: null,
      role: "admin",
      registered_at: "2026-11-01T08:00:00-05:00",
      invitation_code: null,
      last_login_at: "2026-11-05T08:00:00-05:00",
    },
    {
      id: "u-922222222",
      phone: "922222222",
      email: null,
      verified: true,
      pending_code: null,
      delivered_by: null,
      role: "farmer",
      registered_at: "2026-11-05T09:00:00-05:00",
      invitation_code: "DEMO-0001",
      last_login_at: null,
    },
    {
      id: "u-933333333",
      phone: "933333333",
      email: null,
      verified: true,
      pending_code: null,
      delivered_by: null,
      role: "farmer",
      registered_at: "2026-11-02T09:00:00-05:00",
      invitation_code: "DEMO-0002",
      last_login_at: "2026-11-03T10:00:00-05:00",
    },
  ],
};

describe("participantes", () => {
  it("separa al equipo de los caficultores y cuenta quiénes entraron hoy", () => {
    const today = new Date("2026-11-05T00:00:00-05:00");
    const result = summarize(report, today);

    expect(result.farmers.map((p) => p.phone)).toEqual(["922222222", "933333333"]);
    expect(result.team.map((p) => p.phone)).toEqual(["911111111"]);
    expect(result.activeSince).toBe(1);
  });

  it("calcula el comienzo del día", () => {
    const start = startOfToday(new Date(2026, 10, 5, 15, 30));
    expect([start.getHours(), start.getMinutes(), start.getDate()]).toEqual([0, 0, 5]);
  });
});

describe("enviar el código por WhatsApp", () => {
  it("arma el enlace al celular del caficultor con el mensaje listo", async () => {
    const { sendCodeLink } = await import("./participants");
    const link = sendCodeLink("955500111", "932897", (code) => `Tu código es ${code}`);
    expect(link).toBe("https://wa.me/51955500111?text=Tu%20c%C3%B3digo%20es%20932897");
  });
});
