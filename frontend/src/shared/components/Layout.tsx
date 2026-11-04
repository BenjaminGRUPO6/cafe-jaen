import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { PageTransition } from "../motion/PageTransition";
import { texts } from "../texts/es";
import { BottomNav } from "./BottomNav";
import { Brand } from "./Brand";

export function Layout() {
  const { logout, isAdmin } = useAuth();
  return (
    <div className="layout">
      <header className="header">
        <Brand />
        <span className="header__actions">
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
