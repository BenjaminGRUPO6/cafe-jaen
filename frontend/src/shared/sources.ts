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

/** Las webs de la bolsa que consulta la app; primero las que respaldaron el precio mostrado. */
export function quoteSourceLinks(sources: string[]): SourceLink[] {
  const all = Object.values(QUOTE_SOURCES);
  return [
    ...all.filter((link) => sources.includes(link.name)),
    ...all.filter((link) => !sources.includes(link.name)),
  ];
}
