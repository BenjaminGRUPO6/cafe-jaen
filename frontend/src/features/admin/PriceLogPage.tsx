import { useState } from "react";
import type { CoffeeType } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatCents, formatDateTime, formatNumber, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useAutoReload } from "../../shared/hooks/useAutoReload";
import { Segmented } from "../../shared/motion/Segmented";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "./AdminTabs";

interface PriceLogEntry {
  quoted_at: string;
  cents_per_pound: number;
  exchange_rate: number | null;
  price_soles: number | null;
  sources: string[];
  local_soles: Partial<Record<CoffeeType, number>>;
}

const TYPES: CoffeeType[] = ["convencional", "organico", "especial"];
const REFRESH_MS = 30_000; // el Recolector consulta cada minuto

/** Historial de lo que consultó el Recolector (24 h), con el estimado del tipo de café elegido. */
export function PriceLogPage() {
  const { data, error, reload } = useApi<{ entries: PriceLogEntry[] }>(
    "/admin/price-log?limit=120",
  );
  useAutoReload(reload, REFRESH_MS);
  // Una columna por tipo no entra en un celular: se elige el tipo y se muestra su estimado
  const [coffeeType, setCoffeeType] = useState<CoffeeType>("convencional");

  return (
    <section>
      <AdminTabs />
      <h1>{texts.priceLog.title}</h1>
      <p className="muted">{texts.priceLog.intro}</p>
      {!data ? (
        <StatusMessage loading={!error} error={error} onRetry={reload} />
      ) : data.entries.length === 0 ? (
        <p className="card muted">{texts.priceLog.empty}</p>
      ) : (
        <>
          <Segmented
            label={texts.admin.coffeeType}
            value={coffeeType}
            onChange={setCoffeeType}
            options={TYPES.map((type) => ({ value: type, label: texts.local.coffeeTypes[type] }))}
          />
          <div className="price-log" role="region" aria-label={texts.priceLog.title} tabIndex={0}>
            <table>
              <thead>
                <tr>
                  <th scope="col">{texts.priceLog.time}</th>
                  <th scope="col">{texts.priceLog.exchange}</th>
                  <th scope="col" className="price-log__local">
                    {texts.priceLog.local(texts.local.coffeeTypes[coffeeType])}
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.entries.map((entry) => (
                  <tr key={entry.quoted_at}>
                    <th scope="row">
                      {formatDateTime(new Date(entry.quoted_at))}
                      <small>{entry.sources.join(", ")}</small>
                    </th>
                    <td>
                      {entry.price_soles !== null ? formatSoles(entry.price_soles) : "—"}
                      <small>
                        {formatCents(entry.cents_per_pound)}
                        {entry.exchange_rate !== null &&
                          ` · ${texts.priceLog.rate(formatNumber(entry.exchange_rate, 3))}`}
                      </small>
                    </td>
                    <td>
                      {entry.local_soles[coffeeType] !== undefined ? (
                        formatSoles(entry.local_soles[coffeeType])
                      ) : (
                        <small>{texts.priceLog.noEstimate}</small>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
