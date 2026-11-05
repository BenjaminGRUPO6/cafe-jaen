/** Páginas públicas de donde sale cada dato (botones «Fuentes»). */
export interface SourceLink {
  name: string;
  detail: string;
  url: string;
  optional?: boolean; // se lista solo si respaldó el precio (p. ej., Stooq exige clave)
}

// Las claves son los nombres que devuelve la API en `sources`
const QUOTE_SOURCES: Record<string, SourceLink> = {
  "Yahoo Finance": {
    name: "Yahoo Finance",
    detail: "Café C (KC=F), bolsa de Nueva York",
    url: "https://finance.yahoo.com/quote/KC%3DF/",
  },
  Stooq: {
    name: "Stooq",
    detail: "Café C (KC.F), bolsa de Nueva York (exige clave desde 2026)",
    url: "https://stooq.com/q/?s=kc.f",
    optional: true,
  },
  CNBC: {
    name: "CNBC",
    detail: "Café C (@KC.1), bolsa de Nueva York",
    url: "https://www.cnbc.com/quotes/@KC.1",
  },
  TradingView: {
    name: "TradingView",
    detail: "Café C (ICEUS:KC1!), bolsa de Nueva York",
    url: "https://www.tradingview.com/symbols/ICEUS-KC1!/",
  },
};

/** Webs del dólar en vivo (USD/PEN), consultadas cada minuto junto con la bolsa. */
const EXCHANGE_SOURCES: SourceLink[] = [
  {
    name: "Yahoo Finance (USD/PEN)",
    detail: "Dólar en soles, minuto a minuto",
    url: "https://finance.yahoo.com/quote/PEN%3DX/",
  },
  {
    name: "TradingView (USD/PEN)",
    detail: "Dólar en soles, minuto a minuto",
    url: "https://www.tradingview.com/symbols/USDPEN/",
  },
];

/** Fuentes fijas: la bolsa oficial, el dólar en vivo y el tipo de cambio oficial del BCRP. */
export const REFERENCE_SOURCES: SourceLink[] = [
  ...EXCHANGE_SOURCES,
  {
    name: "ICE",
    detail: "Bolsa oficial del contrato Café C (arábica)",
    url: "https://www.ice.com/products/15/Coffee-C-Futures",
  },
  {
    name: "BCRP",
    detail: "Tipo de cambio oficial del día (respaldo si el dólar en vivo no responde)",
    url: "https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/resultados/PD04640PD/html",
  },
];

/** Página pública de una fuente (web de la bolsa o BCRP), por el nombre que guarda la API. */
export function quoteSourceUrl(name: string): string | undefined {
  return (QUOTE_SOURCES[name] ?? REFERENCE_SOURCES.find((link) => link.name === name))?.url;
}

/** Las webs de la bolsa que consulta la app; primero las que respaldaron el precio mostrado. */
export function quoteSourceLinks(sources: string[]): SourceLink[] {
  const all = Object.values(QUOTE_SOURCES);
  return [
    ...all.filter((link) => sources.includes(link.name)),
    ...all.filter((link) => !sources.includes(link.name) && !link.optional),
  ];
}
