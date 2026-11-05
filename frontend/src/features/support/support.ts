/** Mensajes de «Atención» (GET /api/support/messages y /api/admin/support/{id}). */
export interface SupportMessage {
  id: number;
  author: "farmer" | "team";
  text: string;
  created_at: string;
  read: boolean;
}

export interface SupportUser {
  phone: string;
  email: string | null;
  role: "farmer" | "admin";
}

/** Una conversación en la bandeja del equipo. */
export interface SupportThread {
  user_id: string;
  user: SupportUser | null; // null si la cuenta fue eliminada
  last_text: string;
  last_at: string;
  last_author: "farmer" | "team";
  unread: number;
}

export const MAX_LENGTH = 1000; // el mismo tope que valida el backend

/** Resumen de una línea para la bandeja: los mensajes largos se cortan. */
export function preview(text: string, length = 80): string {
  const single = text.replace(/\s+/g, " ").trim();
  return single.length > length ? `${single.slice(0, length - 1)}…` : single;
}
