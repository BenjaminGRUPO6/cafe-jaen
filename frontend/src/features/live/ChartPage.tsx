import { useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { HistoryPeriod, HistoryPoint, PriceHistory } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDate, formatSoles, formatTime } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { texts } from "../../shared/texts/es";

const PERIODS: HistoryPeriod[] = ["today", "30", "90"];

/** HU04: gráfico tipo bolsa: hoy minuto a minuto, o los cierres de 30 y 90 días. */
export function ChartPage() {
  const [period, setPeriod] = useState<HistoryPeriod>("today");
  const { data, error, loading, reload } = useApi<PriceHistory>(`/prices/history?period=${period}`);
  const intraday = period === "today";
  const label = (point: HistoryPoint) =>
    intraday && point.time ? formatTime(point.time) : formatDate(point.date);

  return (
    <section>
      <h1>{texts.chart.title}</h1>
      <div className="segmented">
        {PERIODS.map((option) => (
          <button
            key={option}
            className={`button ${option === period ? "" : "button--secondary"}`}
            onClick={() => setPeriod(option)}
          >
            {texts.chart.periods[option]}
          </button>
        ))}
      </div>
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && !loading && data.points.length === 0 && (
        <p className="status">{texts.chart.empty}</p>
      )}
      {data && !loading && data.points.length > 0 && (
        <div className="card" style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.points.map((point) => ({ ...point, label: label(point) }))}>
              <XAxis
                dataKey="label"
                tickFormatter={(text: string) => (intraday ? text : text.slice(0, 5))}
                minTickGap={24}
              />
              <YAxis domain={["auto", "auto"]} width={56} />
              <Tooltip
                formatter={(value) => [formatSoles(Number(value)), texts.common.perQuintal]}
              />
              <Line
                type="monotone"
                dataKey="price_soles"
                stroke="#3e2723"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
