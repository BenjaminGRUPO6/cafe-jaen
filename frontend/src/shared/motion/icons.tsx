// Íconos de línea simples (sin emojis): se ven igual en todos los celulares
const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export const BeanIcon = () => (
  <svg {...base} strokeWidth={2}>
    <ellipse cx="12" cy="12" rx="6.5" ry="9" transform="rotate(35 12 12)" />
    <path d="M8.2 6.6c3.4 2.6 4.2 7.4 7.6 10.8" />
  </svg>
);
export const RefreshIcon = () => (
  <svg {...base} strokeWidth={2.2}>
    <path d="M20 11a8 8 0 0 0-14.3-4.9L4 8" />
    <path d="M4 4v4h4" />
    <path d="M4 13a8 8 0 0 0 14.3 4.9L20 16" />
    <path d="M20 20v-4h-4" />
  </svg>
);
export const SellIcon = () => (
  <svg {...base} strokeWidth={2.2}>
    <path d="M5 12.5l4.5 4.5L19 7.5" />
  </svg>
);
export const WaitIcon = () => (
  <svg {...base} strokeWidth={2.2}>
    <circle cx="12" cy="12" r="8" />
    <path d="M12 7.5V12l3 2" />
  </svg>
);
export const InfoIcon = () => (
  <svg {...base} strokeWidth={2}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5.5" />
    <path d="M12 7.6v.01" />
  </svg>
);
export const ExternalIcon = () => (
  <svg {...base} strokeWidth={2}>
    <path d="M14 4h6v6" />
    <path d="M20 4l-9 9" />
    <path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" />
  </svg>
);
export const EyeIcon = () => (
  <svg {...base} strokeWidth={2}>
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);
export const EyeOffIcon = () => (
  <svg {...base} strokeWidth={2}>
    <path d="M3 3l18 18" />
    <path d="M10.6 5.1A10.4 10.4 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.1 4.1" />
    <path d="M6.6 6.6C3.9 8.3 2 12 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6" />
    <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
  </svg>
);

// Íconos del kit visual de Café Jaén (64×64, trazo 3). Toman el color del texto (currentColor),
// así se ven bien en la barra oscura, en las pestañas y en las tarjetas claras.
const kit = {
  viewBox: "0 0 64 64",
  fill: "none",
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export const PriceIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M12 18h21l20 14-20 14H12z" />
      <circle cx="20" cy="32" r="3" />
      <path d="M38 25 29 39" />
    </g>
  </svg>
);
export const ChartIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M11 50V15M11 50h43" />
      <path d="m18 39 10-9 9 5 13-18" />
      <path d="M43 17h7v7" />
    </g>
  </svg>
);
export const DecisionIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M32 11v42M24 16c3-4 15-4 17 2 3 9-18 9-18 19 0 10 17 11 20 1" />
      <path d="M13 12 8 21l5 9M51 12l5 9-5 9" />
    </g>
  </svg>
);
export const ForecastIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <rect x="10" y="14" width="44" height="40" rx="6" />
      <path d="M10 26h44M22 9v10M42 9v10" />
      <text
        x="32"
        y="46"
        fontSize="21"
        fontWeight="800"
        fontFamily="Arial"
        textAnchor="middle"
        fill="currentColor"
        stroke="none"
      >
        7
      </text>
    </g>
  </svg>
);
export const AdvisorIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <rect x="9" y="13" width="46" height="36" rx="11" />
      <path d="M20 49v8l10-8" />
      <circle cx="23" cy="30" r="2" fill="currentColor" stroke="none" />
      <circle cx="41" cy="30" r="2" fill="currentColor" stroke="none" />
      <path d="M26 39q6 5 12 0" />
    </g>
  </svg>
);
export const TrashIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M13 19h38M23 19v35h18V19M24 13h16M27 28v18M37 28v18" />
    </g>
  </svg>
);
export const EditIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M14 48 12 55l8-2L52 21 43 12Z" />
      <path d="m39 16 9 9" />
    </g>
  </svg>
);
export const NoSignalIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M7 25c15-14 35-14 50 0M16 35c9-8 23-8 32 0M26 45c4-3 8-3 12 0M32 53h.1M8 8l48 48" />
    </g>
  </svg>
);
export const ProfileIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <circle cx="32" cy="22" r="11" />
      <path d="M10 55c1-23 43-23 44 0" />
    </g>
  </svg>
);
export const HelpIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <circle cx="32" cy="32" r="23" />
      <path d="M24 24c0-12 18-12 18 0 0 8-10 8-10 16" />
      <circle cx="32" cy="48" r="2" fill="currentColor" stroke="none" />
    </g>
  </svg>
);
export const MessagesIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M12 13h40a5 5 0 0 1 5 5v27a5 5 0 0 1-5 5H28L15 58V50h-3a5 5 0 0 1-5-5V18a5 5 0 0 1 5-5Z" />
      <path d="M17 26h29M17 36h21" />
    </g>
  </svg>
);
export const CooperativesIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <circle cx="24" cy="22" r="7" />
      <circle cx="42" cy="22" r="7" />
      <path d="M10 47v-5c0-12 25-12 25 0v5ZM35 47h19v-5c0-7-4-10-10-11" />
    </g>
  </svg>
);
export const CodesIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <rect x="10" y="10" width="17" height="17" rx="2" />
      <rect x="37" y="10" width="17" height="17" rx="2" />
      <rect x="10" y="37" width="17" height="17" rx="2" />
      <path d="M37 37h7v7h-7zm11 11h6v6h-6m-12-6v6m13-17h5" />
    </g>
  </svg>
);
export const ParticipantsIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <circle cx="23" cy="20" r="7" />
      <circle cx="45" cy="24" r="5" />
      <path d="M8 50v-5c0-15 29-15 29 0v5ZM40 35c11-3 16 4 16 10v5H42" />
    </g>
  </svg>
);
export const ExchangeIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M10 50h44M16 44l10-14 9 6 14-22" />
      <path d="M41 14h8v8" />
    </g>
  </svg>
);
export const AdminPricesIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M9 19h43M9 32h43M9 45h43" />
      <circle cx="22" cy="19" r="5" className="icon-knock" />
      <circle cx="43" cy="32" r="5" className="icon-knock" />
      <circle cx="29" cy="45" r="5" className="icon-knock" />
    </g>
  </svg>
);
export const EmptyDataIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <path d="M19 9h21l12 12v34H19zM40 9v12h12M25 33h20M25 42h12" />
      <circle cx="46" cy="49" r="10" className="icon-knock" />
      <path d="m53 56 6 6" />
    </g>
  </svg>
);
export const EmptyMessagesIcon = () => (
  <svg {...kit}>
    <g stroke="currentColor" strokeWidth="3" fill="none">
      <rect x="9" y="16" width="46" height="33" rx="6" />
      <path d="m11 21 21 17 21-17M45 9h12M51 3v12" />
    </g>
  </svg>
);
