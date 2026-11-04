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

export const PriceIcon = () => (
  <svg {...base}>
    <ellipse cx="12" cy="12" rx="6" ry="8.5" transform="rotate(-30 12 12)" />
    <path d="M9.5 6.5c2.5 3 2.5 8 -1 11" />
  </svg>
);
export const ChartIcon = () => (
  <svg {...base}>
    <path d="M4 19h16" />
    <path d="M5 15l4-5 4 3 6-7" />
  </svg>
);
export const DecisionIcon = () => (
  <svg {...base}>
    <path d="M12 4v16" />
    <path d="M5 8h14" />
    <path d="M5 8l-2.5 6a3 3 0 0 0 5 0z" />
    <path d="M19 8l-2.5 6a3 3 0 0 0 5 0z" />
  </svg>
);
export const ForecastIcon = () => (
  <svg {...base}>
    <rect x="4" y="5" width="16" height="15" rx="2" />
    <path d="M4 10h16M9 3v4M15 3v4" />
    <path d="M8 15l2.5-2 2.5 1.5 3-2.5" />
  </svg>
);
export const AdvisorIcon = () => (
  <svg {...base}>
    <path d="M5 5h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-8l-4 3v-3H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z" />
  </svg>
);
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
export const NoSignalIcon = () => (
  <svg {...base} strokeWidth={2.2}>
    <path d="M6 12h12" />
  </svg>
);
