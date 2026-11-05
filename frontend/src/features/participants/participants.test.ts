import { describe, expect, it } from "vitest";
import { startOfToday, summarize, type ParticipantsReport } from "./participants";

const report: ParticipantsReport = {
  codes: { total: 10, used: 2 },
  participants: [
    {
      phone: "911111111",
      role: "admin",
      registered_at: "2026-11-01T08:00:00-05:00",
      invitation_code: null,
      last_login_at: "2026-11-05T08:00:00-05:00",
    },
    {
      phone: "922222222",
      role: "farmer",
      registered_at: "2026-11-05T09:00:00-05:00",
      invitation_code: "DEMO-0001",
      last_login_at: null,
    },
    {
      phone: "933333333",
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
