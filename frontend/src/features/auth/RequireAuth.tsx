import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../shared/auth/AuthContext";

/** Solo deja pasar a quien tiene sesión; si no, lo lleva a ingresar. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? children : <Navigate to="/ingresar" replace />;
}
