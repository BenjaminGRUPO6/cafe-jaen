import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";
import { AdvisorIcon, ChartIcon, DecisionIcon, ForecastIcon, PriceIcon } from "../motion/icons";
import { texts } from "../texts/es";

const ITEMS = [
  { to: "/", label: texts.nav.live, Icon: PriceIcon },
  { to: "/grafico", label: texts.nav.chart, Icon: ChartIcon },
  { to: "/vender", label: texts.nav.decision, Icon: DecisionIcon },
  { to: "/pronostico", label: texts.nav.forecast, Icon: ForecastIcon },
  { to: "/asesor", label: texts.nav.advisor, Icon: AdvisorIcon },
];

/** Navegación inferior: cualquier pantalla está a un solo toque (RNF02). */
export function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Navegación principal">
      <div className="bottom-nav__inner">
        {ITEMS.map(({ to, label, Icon }) => (
          <NavLink key={to} to={to} end className="bottom-nav__item">
            {({ isActive }) => (
              <>
                {/* El fondo de la pestaña activa se desliza a la pestaña tocada */}
                {isActive && (
                  <motion.span
                    layoutId="bottom-nav-pill"
                    className="bottom-nav__pill"
                    transition={{ type: "spring", stiffness: 420, damping: 36 }}
                  />
                )}
                <Icon />
                <span className="bottom-nav__label">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
