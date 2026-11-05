import type { HistoryPoint } from "../../shared/api/types";

const MINUTE = 60_000;
const DAY = 24 * 60 * MINUTE;
const LIMA_OFFSET = -5 * 60 * MINUTE; // Lima: UTC-5 todo el año (sin horario de verano)
const WEEKDAYS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

/** Un punto del gráfico con su instante real (ms), para que el eje respete el tiempo. */
export interface TimedPoint {
  at: number;
  price_soles: number;
}

/**
 * Los días del histórico llegan como «AAAA-MM-DD»: se ubican al mediodía de Lima para que
 * ninguna zona horaria los corra al día anterior.
 */
export function toTimed(points: HistoryPoint[], intraday: boolean): TimedPoint[] {
  return points.map((point) => ({
    at:
      intraday && point.time
        ? new Date(point.time).getTime()
        : Date.parse(`${point.date}T12:00:00-05:00`),
    price_soles: point.price_soles,
  }));
}

/**
 * Marcas del eje a intervalos parejos y redondos: cada 15, 30 o 60 minutos en «Hoy» y cada
 * 7 o 28 días en los históricos (los lunes), según el largo del periodo.
 */
export function timeTicks(start: number, end: number, intraday: boolean): number[] {
  if (end <= start) return [start];
  const span = end - start;
  if (intraday) {
    const minutes = span <= 90 * MINUTE ? 15 : span <= 3 * 60 * MINUTE ? 30 : 60;
    const step = minutes * MINUTE;
    return range(Math.ceil(start / step) * step, end, step);
  }
  const step = (span <= 45 * DAY ? 7 : 28) * DAY;
  return range(nextMondayNoon(start), end, step);
}

/** «10:30» en hora de Lima. */
export function tickTime(at: number): string {
  const lima = inLima(at);
  return `${pad(lima.getUTCHours())}:${pad(lima.getUTCMinutes())}`;
}

/** «13/10» en hora de Lima. */
export function tickDay(at: number): string {
  const lima = inLima(at);
  return `${pad(lima.getUTCDate())}/${pad(lima.getUTCMonth() + 1)}`;
}

/** «Lun 13/10» o «13/10 10:30» para la ayuda que aparece al tocar el gráfico. */
export function tooltipLabel(at: number, intraday: boolean): string {
  if (intraday) return `${tickDay(at)} ${tickTime(at)}`;
  return `${WEEKDAYS[inLima(at).getUTCDay()]} ${tickDay(at)}`;
}

/** Minutos entre la última cotización y ahora (retraso real que se muestra al caficultor). */
export function delayMinutes(lastAt: number, now: number): number {
  return Math.max(0, Math.round((now - lastAt) / MINUTE));
}

// Fecha «corrida» a la hora de Lima: se lee con los métodos UTC (igual en cualquier navegador)
function inLima(at: number): Date {
  return new Date(at + LIMA_OFFSET);
}

function nextMondayNoon(at: number): number {
  let noon = Math.floor((at - LIMA_OFFSET) / DAY) * DAY + 12 * 60 * MINUTE - LIMA_OFFSET;
  if (noon < at) noon += DAY;
  while (inLima(noon).getUTCDay() !== 1) noon += DAY;
  return noon;
}

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

function range(first: number, end: number, step: number): number[] {
  const ticks = [];
  for (let at = first; at <= end; at += step) ticks.push(at);
  return ticks;
}
