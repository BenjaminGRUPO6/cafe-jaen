import { NavLink } from "react-router-dom";
import {
  AdminPricesIcon,
  CodesIcon,
  CooperativesIcon,
  ExchangeIcon,
  MessagesIcon,
  ParticipantsIcon,
} from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";

const TABS = [
  { to: "/equipo", label: texts.admin.tabPrices, Icon: AdminPricesIcon },
  { to: "/equipo/cooperativas", label: texts.cooperatives.tab, Icon: CooperativesIcon },
  { to: "/equipo/codigos", label: texts.codes.tab, Icon: CodesIcon },
  { to: "/equipo/participantes", label: texts.participants.tab, Icon: ParticipantsIcon },
  { to: "/equipo/bolsa", label: texts.priceLog.tab, Icon: ExchangeIcon },
  { to: "/equipo/mensajes", label: texts.support.tab, Icon: MessagesIcon },
];

/** Pestañas del área del equipo, con su ícono para encontrarlas de un vistazo. */
export function AdminTabs() {
  return (
    <nav className="admin-tabs" aria-label={texts.admin.nav}>
      {TABS.map(({ to, label, Icon }) => (
        <NavLink key={to} to={to} end className="admin-tabs__link">
          <Icon />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
