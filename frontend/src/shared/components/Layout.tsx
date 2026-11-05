import { Link, Outlet, useLocation } from "react-router-dom";
import { useApi } from "../hooks/useApi";
import { useAutoReload } from "../hooks/useAutoReload";
import { useAuth } from "../auth/AuthContext";
import { PageTransition } from "../motion/PageTransition";
import { texts } from "../texts/es";
import { BottomNav } from "./BottomNav";
import { Brand } from "./Brand";

export function Layout() {
  const { logout, isAdmin } = useAuth();
  // Aviso de respuestas nuevas del equipo en «Ayuda». La pantalla va en la consulta solo para
  // que se repita al navegar (la API la ignora); dentro de «Ayuda» ya se están leyendo.
  const { pathname } = useLocation();
  const { data: support, reload } = useApi<{ unread: number }>(
    `/support/unread?pantalla=${encodeURIComponent(pathname)}`,
  );
  useAutoReload(reload, 60_000);
  const unread = pathname === "/ayuda" ? 0 : (support?.unread ?? 0);
  return (
    <div className="layout">
      <header className="header">
        <Brand />
        <span className="header__actions">
          <Link to="/ayuda" className="link-button header__link">
            {texts.support.nav}
            {unread > 0 && (
              <span className="badge" aria-label={texts.support.newReplies(unread)}>
                {unread}
              </span>
            )}
          </Link>
          {isAdmin && (
            <Link to="/equipo" className="link-button header__link">
              {texts.admin.nav}
            </Link>
          )}
          <button className="link-button" onClick={logout}>
            {texts.common.logout}
          </button>
        </span>
      </header>
      <main className="content">
        <PageTransition>
          <Outlet />
        </PageTransition>
      </main>
      <BottomNav />
    </div>
  );
}
