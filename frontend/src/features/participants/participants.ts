/** Respuesta de GET /api/admin/participants (solo el equipo). */
export interface Participant {
  id: string;
  phone: string;
  email: string | null;
  verified: boolean;
  pending_code: string | null; // código por confirmar: el equipo lo envía si el correo no llegó
  delivered_by: "whatsapp" | "email" | null;
  role: "farmer" | "admin";
  registered_at: string;
  invitation_code: string | null;
  last_login_at: string | null;
}

export interface ParticipantsReport {
  codes: { total: number; used: number };
  participants: Participant[];
}

/** Participantes del GE (sin las cuentas del equipo) y cuántos entraron desde `since`. */
export function summarize(report: ParticipantsReport, since: Date) {
  const farmers = report.participants.filter((p) => p.role === "farmer");
  const activeSince = farmers.filter((p) => {
    const last = p.last_login_at ?? p.registered_at;
    return new Date(last).getTime() >= since.getTime();
  }).length;
  return { farmers, team: report.participants.filter((p) => p.role === "admin"), activeSince };
}

/** Comienzo del día de hoy (hora local del celular). */
export function startOfToday(now: Date): Date {
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

/** Abre WhatsApp con el código listo para enviárselo al caficultor desde el celular del equipo. */
export function sendCodeLink(
  phone: string,
  code: string,
  message: (code: string) => string,
): string {
  return `https://wa.me/51${phone}?text=${encodeURIComponent(message(code))}`;
}
