import type { Forecast } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDate, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { texts } from "../../shared/texts/es";

/** HU06: pronóstico a 7 días hábiles con su rango y el aviso de que es referencial. */
export function ForecastPage() {
  const { data, error, loading, reload } = useApi<Forecast>("/forecast");

  return (
    <section>
      <h1>{texts.forecast.title}</h1>
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <article className="card">
          <p className="banner">{data.disclaimer}</p>
          <table className="table">
            <thead>
              <tr>
                <th>{texts.forecast.day}</th>
                <th>{texts.forecast.expected}</th>
                <th>{texts.forecast.range}</th>
              </tr>
            </thead>
            <tbody>
              {data.points.map((point) => (
                <tr key={point.date}>
                  <td>{formatDate(point.date).slice(0, 5)}</td>
                  <td className="nowrap">
                    <strong>{formatSoles(point.expected_soles)}</strong>
                  </td>
                  <td className="muted">
                    {formatSoles(point.lower_soles)} – {formatSoles(point.upper_soles)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      )}
    </section>
  );
}
