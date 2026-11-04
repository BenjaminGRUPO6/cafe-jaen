import type { ForecastPoint, LocalEstimate } from "../../shared/api/types";

/** Un día del pronóstico expresado en el precio de la bolsa y, si hay datos, en Jaén. */
export interface LocalForecastPoint extends ForecastPoint {
  local_soles: number | null;
}

/**
 * Pronóstico estimado en Jaén = pronóstico de la bolsa × porcentaje que pagan las
 * cooperativas por ese tipo de café (el mismo cálculo que el precio estimado de hoy, HU12).
 * Así el caficultor ve el pronóstico en el mismo precio que predice en la ficha de la TPP.
 */
export function toLocalForecast(
  points: ForecastPoint[],
  estimate: LocalEstimate | undefined,
): LocalForecastPoint[] {
  return points.map((point) => ({
    ...point,
    local_soles: estimate ? roundCents((point.expected_soles * estimate.ratio_pct) / 100) : null,
  }));
}

function roundCents(value: number): number {
  return Math.round(value * 100) / 100;
}
