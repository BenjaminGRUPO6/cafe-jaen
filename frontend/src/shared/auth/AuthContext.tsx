import { createContext, useContext, useState, type ReactNode } from "react";
import { api, TOKEN_KEY } from "../api/client";
import type { Session } from "../api/types";
import { readStored, writeStored } from "../storage";

interface RegisterData {
  invitation_code: string;
  phone: string;
  password: string;
  consent_accepted: boolean;
}

interface AuthState {
  isLoggedIn: boolean;
  isAdmin: boolean;
  login: (phone: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

/** Guarda la sesión (30 días) para que el caficultor no tenga que ingresar cada vez. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => readStored(TOKEN_KEY));

  const saveSession = (session: Session) => {
    writeStored(TOKEN_KEY, session.access_token);
    setToken(session.access_token);
  };

  const value: AuthState = {
    isLoggedIn: token !== null,
    isAdmin: roleFromToken(token) === "admin",
    login: async (phone, password) =>
      saveSession(await api.post<Session>("/auth/login", { phone, password })),
    register: async (data) => saveSession(await api.post<Session>("/auth/register", data)),
    logout: () => {
      writeStored(TOKEN_KEY, null);
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
