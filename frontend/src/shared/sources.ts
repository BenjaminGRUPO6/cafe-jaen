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

/**
 * Enlaces de las webs que respaldaron un precio. En modo demostración el precio es sintético,
 * así que se muestran todas las webs que la app consulta con datos reales.
 */
export function quoteSourceLinks(sources: string[]): SourceLink[] {
  if (isDemoSource(sources)) return Object.values(QUOTE_SOURCES);
  return sources.flatMap((source) => (QUOTE_SOURCES[source] ? [QUOTE_SOURCES[source]] : []));
}

export function isDemoSource(sources: string[]): boolean {
  return sources.some((source) => source.startsWith("DEMO"));
}
