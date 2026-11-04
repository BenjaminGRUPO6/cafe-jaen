import { motion } from "framer-motion";
import type { Forecast, LivePrice } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatPercent, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useCoffeeType } from "../../shared/hooks/useCoffeeType";
import { Segmented } from "../../shared/motion/Segmented";
import { texts } from "../../shared/texts/es";
import { toLocalForecast } from "./localForecast";

const WEEKDAYS = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];

/**
 * HU06: pronóstico a 7 días hábiles con su rango y el aviso de que es referencial.
 * Muestra también el estimado en Jaén por tipo de café: es el precio que el caficultor
 * predice en la ficha de la TPP (S/ por quintal de pergamino).
 */
export function ForecastPage() {
  const { data, error, loading, reload } = useApi<Forecast>("/forecast");
  const { data: live } = useApi<LivePrice>("/prices/live");
  const [chosen, choose] = useCoffeeType();
  const estimates = live?.local_estimates ?? [];
  const estimate = estimates.find((e) => e.coffee_type === chosen) ?? estimates[0];

  return (
    <section>
      <h1>{texts.forecast.title}</h1>
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <>
          {estimates.length > 1 && estimate && (
            <Segmented
              label={texts.local.title}
              value={estimate.coffee_type}
              onChange={choose}
              options={estimates.map((e) => ({
                value: e.coffee_type,
                label: texts.local.coffeeTypes[e.coffee_type],
              }))}
            />
          )}
          <article className="card">
            <p className="banner">{data.disclaimer}</p>
            <ForecastList forecast={data} estimate={estimate} />
          </article>
          <p className="footnote">
            {estimate
              ? texts.forecast.localNote(
                  formatPercent(estimate.ratio_pct),
                  texts.local.coffeeTypes[estimate.coffee_type].toLowerCase(),
                )
              : texts.forecast.noLocal}{" "}
            {texts.forecast.rangeHint}
          </p>
        </>
      )}
    </section>
  );
}

function ForecastList({
  forecast,
  estimate,
}: {
  forecast: Forecast;
  estimate: Parameters<typeof toLocalForecast>[1];
}) {
  const points = toLocalForecast(forecast.points, estimate);
  // La escala de las barras cubre todos los rangos de la semana
  const low = Math.min(...points.map((p) => p.lower_soles));
  const high = Math.max(...points.map((p) => p.upper_soles));
  const position = (value: number) => ((value - low) / (high - low || 1)) * 100;

  return (
    <ol className="forecast">
      {points.map((point, index) => {
        const [year, month, day] = point.date.split("-").map(Number);
        const weekday = WEEKDAYS[new Date(year, month - 1, day).getDay()];
        return (
          <li key={point.date} className="forecast__row">
            <span className="forecast__day">
              {weekday}
              <small>
                {String(day).padStart(2, "0")}/{String(month).padStart(2, "0")}
              </small>
            </span>
            <span className="forecast__values">
              <span className="forecast__range" aria-hidden="true">
                <motion.span
                  className="forecast__band"
                  style={{ left: `${position(point.lower_soles)}%` }}
                  initial={{ width: 0 }}
                  animate={{
                    width: `${position(point.upper_soles) - position(point.lower_soles)}%`,
                  }}
                  transition={{ delay: index * 0.05, type: "spring", stiffness: 200, damping: 26 }}
                />
                <span
                  className="forecast__dot"
                  style={{ left: `${position(point.expected_soles)}%` }}
                />
              </span>
              <span className="forecast__exchange">
                {texts.forecast.exchange} {formatSoles(point.expected_soles)}
                <br />
                {texts.forecast.range(point.lower_soles.toFixed(0), point.upper_soles.toFixed(0))}
              </span>
            </span>
            {point.local_soles !== null ? (
              <span className="forecast__local">
                {formatSoles(point.local_soles)}
                <small>{texts.forecast.jaen}</small>
              </span>
            ) : (
              <span className="forecast__local">{formatSoles(point.expected_soles)}</span>
            )}
          </li>
        );
      })}
    </ol>
  );
}
