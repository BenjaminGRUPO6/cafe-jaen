import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../shared/auth/AuthContext";

/** Pantalla del equipo: a los caficultores los regresa al precio (la API también lo impide). */
export function RequireAdmin({ children }: { children: ReactNode }) {
  const { isAdmin } = useAuth();
  return isAdmin ? children : <Navigate to="/" replace />;
}
