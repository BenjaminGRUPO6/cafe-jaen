import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { texts } from "../texts/es";
import { BottomNav } from "./BottomNav";

export function Layout() {
  const { logout, isAdmin } = useAuth();
  return (
    <div className="layout">
      <header className="header">
        <span className="header__title">☕ {texts.appName}</span>
        <span>
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
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
