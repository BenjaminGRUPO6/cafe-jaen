import { NavLink } from "react-router-dom";
import { texts } from "../texts/es";

const ITEMS = [
  { to: "/", label: texts.nav.live, icon: "☕" },
  { to: "/grafico", label: texts.nav.chart, icon: "📈" },
  { to: "/vender", label: texts.nav.decision, icon: "⚖️" },
  { to: "/pronostico", label: texts.nav.forecast, icon: "🔮" },
  { to: "/asesor", label: texts.nav.advisor, icon: "💬" },
];

/** Navegación inferior: cualquier pantalla está a un solo toque (RNF02). */
export function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Navegación principal">
      {ITEMS.map((item) => (
        <NavLink key={item.to} to={item.to} end className="bottom-nav__item">
          <span aria-hidden="true">{item.icon}</span>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
