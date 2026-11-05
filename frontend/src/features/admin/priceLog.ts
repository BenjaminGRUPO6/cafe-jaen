import type { CoffeeType } from "../../shared/api/types";

/** Lo que marcó una web en una consulta (GET /api/admin/price-log). */
export interface SourceReading {
  source: string;
  status: "usada" | "descartada" | "sin respuesta";
  cents_per_pound: number | null;
  quoted_at: string | null;
  deviation_pct: number | null;
  detail: string | null;
}

export interface PriceLogEntry {
  quoted_at: string;
  published: boolean;
  cents_per_pound: number | null;
  median_cents: number | null;
  exchange_rate: number | null;
  price_soles: number | null;
  sources: string[];
  local_soles: Partial<Record<CoffeeType, number>>;
  readings: SourceReading[];
}

export interface DaySummary {
  collections: number;
  published: number;
  withDiscarded: number;
  withFailures: number;
}

/** Resumen del día: cuántas consultas hubo y en cuántas alguna web se descartó o no respondió. */
export function summarizeDay(entries: PriceLogEntry[]): DaySummary {
  const has = (entry: PriceLogEntry, status: SourceReading["status"]) =>
    entry.readings.some((reading) => reading.status === status);
  return {
    collections: entries.length,
    published: entries.filter((entry) => entry.published).length,
    withDiscarded: entries.filter((entry) => has(entry, "descartada")).length,
    withFailures: entries.filter((entry) => has(entry, "sin respuesta")).length,
  };
}

/** Fecha de hoy en el formato del campo de fecha (AAAA-MM-DD, hora local del navegador). */
export function todayInput(now: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}
