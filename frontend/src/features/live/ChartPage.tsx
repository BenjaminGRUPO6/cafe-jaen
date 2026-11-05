import { useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryPeriod, HistoryPoint, PriceHistory } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatPercent, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useNow } from "../../shared/hooks/useNow";
import { Segmented } from "../../shared/motion/Segmented";
import { texts } from "../../shared/texts/es";
import { delayMinutes, tickDay, tickTime, timeTicks, toTimed, tooltipLabel } from "./chartAxis";

const PERIODS: HistoryPeriod[] = ["today", "30", "90"];
const INK = "#1a1208";
const GRANO = "#ffc531";
const MUTED = "#5f574d";

/** HU04: gráfico tipo bolsa: hoy minuto a minuto, o los cierres de 30 y 90 días. */
export function ChartPage() {
  const [period, setPeriod] = useState<HistoryPeriod>("today");
  const { data, error, loading, reload } = useApi<PriceHistory>(`/prices/history?period=${period}`);
  const intraday = period === "today";
  const now = useNow();
  const points = data?.points ?? [];
  // Cada punto en su instante real: el eje respeta los fines de semana y los minutos sin datos
  const timed = toTimed(points, intraday);
  const first = timed[0]?.at ?? 0;
  const last = timed[timed.length - 1]?.at ?? 0;
  const tickFormatter = intraday ? tickTime : tickDay;

  return (
    <section>
      <h1>{texts.chart.title}</h1>
      <Segmented
        label={texts.chart.title}
        value={period}
        onChange={setPeriod}
        options={PERIODS.map((option) => ({ value: option, label: texts.chart.periods[option] }))}
      />
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && !loading && points.length === 0 && <p className="status">{texts.chart.empty}</p>}
      {data && !loading && points.length > 0 && (
        <>
          <Summary points={points} />
          <div className="card chart-card">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timed}>
                <defs>
                  <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={GRANO} stopOpacity={0.9} />
                    <stop offset="100%" stopColor={GRANO} stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="#e3e1d8" />
                <XAxis
                  dataKey="at"
                  type="number"
                  scale="time"
                  domain={[first, last]}
                  ticks={timeTicks(first, last, intraday)}
                  interval={0}
                  tickFormatter={tickFormatter}
                  stroke={MUTED}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={["auto", "auto"]}
                  width={56}
                  stroke={MUTED}
                  tickLine={false}
                  axisLine={false}
                  // Coma decimal, como en el resto de la app
                  tickFormatter={(value: number) =>
                    Number.isInteger(value) ? String(value) : value.toFixed(1).replace(".", ",")
                  }
                />
                <Tooltip
                  labelFormatter={(value) => tooltipLabel(Number(value), intraday)}
                  formatter={(value) => [formatSoles(Number(value)), texts.common.perQuintal]}
                />
                <Area
                  type="linear"
                  dataKey="price_soles"
                  stroke={INK}
                  strokeWidth={2.5}
                  fill="url(#priceFill)"
                  animationDuration={700}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="footnote">
            {intraday
              ? texts.chart.intradayNote(tickTime(last), delayMinutes(last, now))
              : texts.chart.dailyNote(tickDay(first), tickDay(last))}
          </p>
        </>
      )}
    </section>
  );
}

/** Máximo, mínimo y variación del periodo elegido, para leer el gráfico de un vistazo. */
function Summary({ points }: { points: HistoryPoint[] }) {
  const values = points.map((point) => point.price_soles);
  const first = values[0];
  const last = values[values.length - 1];
  const changePct = ((last - first) / first) * 100;
  return (
    <div className="stats">
      <div className="stat">
        <span className="stat__label">{texts.chart.high}</span>
        <span className="stat__value">{formatSoles(Math.max(...values))}</span>
      </div>
      <div className="stat">
        <span className="stat__label">{texts.chart.low}</span>
        <span className="stat__value">{formatSoles(Math.min(...values))}</span>
      </div>
      <div className="stat">
        <span className="stat__label">{texts.chart.change}</span>
        <span className={`stat__value ${changePct >= 0 ? "up" : "down"}`}>
          {changePct >= 0 ? "▲" : "▼"} {formatPercent(Math.abs(changePct))}
        </span>
      </div>
    </div>
  );
}
