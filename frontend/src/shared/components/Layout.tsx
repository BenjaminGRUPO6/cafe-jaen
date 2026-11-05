import { Link, Outlet, useLocation } from "react-router-dom";
import type { Profile } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { useApi } from "../hooks/useApi";
import { useAutoReload } from "../hooks/useAutoReload";
import { HelpIcon, ProfileIcon } from "../motion/icons";
import { PageTransition } from "../motion/PageTransition";
import { texts } from "../texts/es";
import { BottomNav } from "./BottomNav";
import { Brand } from "./Brand";

export function Layout() {
  const { logout, isAdmin } = useAuth();
  const { pathname } = useLocation();
  const { data: profile } = useApi<Profile>("/auth/me");

  return (
    <div className="layout">
      <header className="header">
        <Brand />
        <span className="header__actions">
          {/* El equipo responde en «Equipo → Mensajes»; «Ayuda» es para los caficultores */}
          {isAdmin ? (
            <Link to="/equipo" className="link-button header__link">
              {texts.admin.nav}
            </Link>
          ) : (
            <HelpLink pathname={pathname} />
          )}
          <button className="link-button" onClick={logout}>
            {texts.common.logout}
          </button>
        </span>
      </header>
      {profile && (
        <p className="profile-bar" aria-label={texts.profile.label}>
          <ProfileIcon />
          <strong>{profile.display_name}</strong>
          <span className={`role-chip role-chip--${profile.role}`}>
            {texts.profile.roles[profile.role]}
          </span>
        </p>
      )}
      <main className="content">
        <PageTransition>
          <Outlet />
        </PageTransition>
      </main>
      <BottomNav />
    </div>
  );
}

/** «Ayuda» con el aviso de respuestas nuevas del equipo. */
function HelpLink({ pathname }: { pathname: string }) {
  // La pantalla va en la consulta solo para que se repita al navegar (la API la ignora)
  const { data, reload } = useApi<{ unread: number }>(
    `/support/unread?pantalla=${encodeURIComponent(pathname)}`,
  );
  useAutoReload(reload, 60_000);
  const unread = pathname === "/ayuda" ? 0 : (data?.unread ?? 0); // dentro de «Ayuda» ya se leen
  return (
    <Link to="/ayuda" className="link-button header__link header__help">
      <HelpIcon />
      {texts.support.nav}
      {unread > 0 && (
        <span className="badge" aria-label={texts.support.newReplies(unread)}>
          {unread}
        </span>
      )}
    </Link>
  );
}
