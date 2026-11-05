/** Páginas públicas de donde sale cada dato (botones «Fuentes»). */
export interface SourceLink {
  name: string;
  detail: string;
  url: string;
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
    detail: "Café C (KC.F), bolsa de Nueva York",
    url: "https://stooq.com/q/?s=kc.f",
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

/** Fuentes fijas: la bolsa oficial y el tipo de cambio del BCRP. */
export const REFERENCE_SOURCES: SourceLink[] = [
  {
    name: "ICE",
    detail: "Bolsa oficial del contrato Café C (arábica)",
    url: "https://www.ice.com/products/15/Coffee-C-Futures",
  },
  {
    name: "BCRP",
    detail: "Tipo de cambio interbancario (venta)",
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
    ...all.filter((link) => !sources.includes(link.name)),
  ];
}
