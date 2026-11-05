import { createContext, useContext, useState, type ReactNode } from "react";
import { api, TOKEN_KEY } from "../api/client";
import type { PendingVerification, Session } from "../api/types";
import { readSession, writeSession } from "../storage";

interface RegisterData {
  invitation_code: string;
  phone: string;
  email?: string; // opcional
  name?: string;
  password: string;
  consent_accepted: boolean;
}

interface AuthState {
  isLoggedIn: boolean;
  isAdmin: boolean;
  /** `identifier` es el celular o el correo. */
  login: (identifier: string, password: string) => Promise<void>;
  /** Crea la cuenta sin sesión: luego hay que confirmar el código del correo. */
  register: (data: RegisterData) => Promise<PendingVerification>;
  verify: (phone: string, code: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

/**
 * Guarda la sesión (30 días) para que el caficultor no tenga que ingresar cada vez. Cada
 * pestaña tiene la suya: dos cuentas abiertas en el mismo navegador no se mezclan.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => readSession(TOKEN_KEY));

  const saveSession = (session: Session) => {
    writeSession(TOKEN_KEY, session.access_token);
    setToken(session.access_token);
  };

  const value: AuthState = {
    isLoggedIn: token !== null,
    isAdmin: roleFromToken(token) === "admin",
    login: async (identifier, password) =>
      saveSession(await api.post<Session>("/auth/login", { identifier, password })),
    register: (data) => api.post<PendingVerification>("/auth/register", data),
    verify: async (phone, code) =>
      saveSession(await api.post<Session>("/auth/verify", { phone, code })),
    logout: () => {
      writeSession(TOKEN_KEY, null);
      setToken(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Lee el rol guardado en el token (JWT) solo para mostrar u ocultar la pantalla del equipo.
 * La API es la que realmente protege esas rutas (responde 403 a quien no es administrador).
 */
export function roleFromToken(token: string | null): string | null {
  try {
    const payload = token?.split(".")[1];
    if (!payload) return null;
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    const role = (JSON.parse(json) as { role?: unknown }).role;
    return typeof role === "string" ? role : null;
  } catch {
    return null;
  }
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return context;
}
