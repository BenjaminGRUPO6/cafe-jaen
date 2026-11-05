import { NavLink } from "react-router-dom";
import { texts } from "../../shared/texts/es";

/** Pestañas del área del equipo: precios de cooperativas y participantes del GE. */
export function AdminTabs() {
  return (
    <nav className="admin-tabs" aria-label={texts.admin.nav}>
      <NavLink to="/equipo" end className="admin-tabs__link">
        {texts.admin.tabPrices}
      </NavLink>
      <NavLink to="/equipo/participantes" className="admin-tabs__link">
        {texts.participants.tab}
      </NavLink>
    </nav>
  );
}
