import { NavLink } from "react-router-dom";
import { texts } from "../../shared/texts/es";

const TABS = [
  { to: "/equipo", label: texts.admin.tabPrices },
  { to: "/equipo/cooperativas", label: texts.cooperatives.tab },
  { to: "/equipo/codigos", label: texts.codes.tab },
  { to: "/equipo/participantes", label: texts.participants.tab },
  { to: "/equipo/bolsa", label: texts.priceLog.tab },
  { to: "/equipo/mensajes", label: texts.support.tab },
];

/** Pestañas del área del equipo; en pantallas angostas se desplazan de lado. */
export function AdminTabs() {
  return (
    <nav className="admin-tabs" aria-label={texts.admin.nav}>
      {TABS.map((tab) => (
        <NavLink key={tab.to} to={tab.to} end className="admin-tabs__link">
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
