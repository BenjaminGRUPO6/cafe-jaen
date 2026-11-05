import { useState } from "react";
import type { CoffeeType } from "../../shared/api/types";
import { InfoNote } from "../../shared/components/InfoNote";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatCents, formatDateTime, formatNumber, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useAutoReload } from "../../shared/hooks/useAutoReload";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "./AdminTabs";
import { summarizeDay, todayInput, type PriceLog, type PriceLogEntry } from "./priceLog";
import { SourceRanking } from "./SourceRanking";
import { SourceReadings } from "./SourceReadings";
import { SourceName } from "../../shared/components/SourceName";

const TYPES: CoffeeType[] = ["convencional", "organico", "especial"];
const REFRESH_MS = 30_000; // el Recolector consulta cada minuto
const PAGE = 100; // filas que se muestran antes de «Mostrar más»

/**
 * Historial minuto a minuto de la bolsa en un día: precio publicado, estimado en Jaén del tipo
 * de café elegido y, en cada fila, lo que marcó cada web (por qué se publicó ese precio).
 */
export function PriceLogPage() {
  const today = todayInput(new Date());
  const [day, setDay] = useState(today);
  const [visible, setVisible] = useState(PAGE);
  const { data, error, reload } = useApi<PriceLog>(`/admin/price-log?day=${day}`);
  useAutoReload(reload, REFRESH_MS);
  const summary = data ? summarizeDay(data.entries) : null;

  return (
    <section>
      <AdminTabs />
      <h1>{texts.priceLog.title}</h1>
      <p className="muted">{texts.priceLog.intro}</p>
      <InfoNote label={texts.priceLog.howChosen}>
        <ol>
          {texts.priceLog.howChosenSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </InfoNote>
      <div className="price-log__controls">
        <label className="price-log__day">
          {texts.priceLog.day}
          <input
            type="date"
            value={day}
            max={today}
            onChange={(event) => {
              setDay(event.target.value || today);
              setVisible(PAGE);
            }}
          />
        </label>
      </div>
      {!data || !summary ? (
        <StatusMessage loading={!error} error={error} onRetry={reload} />
      ) : data.entries.length === 0 ? (
        <p className="card muted">{texts.priceLog.empty}</p>
      ) : (
        <>
          <div className="stats">
            <Stat label={texts.priceLog.collections} value={String(summary.collections)} />
            <Stat label={texts.priceLog.withDiscarded} value={String(summary.withDiscarded)} />
            <Stat label={texts.priceLog.withFailures} value={String(summary.withFailures)} />
          </div>
          <SourceRanking ranking={data.ranking} />
          <ul className="price-log" aria-label={texts.priceLog.title}>
            {data.entries.slice(0, visible).map((entry, index) => (
              <LogRow
                key={`${entry.quoted_at}-${index}`}
                entry={entry}
                latest={index === 0 && day === today}
              />
            ))}
          </ul>
          {visible < data.entries.length && (
            <button
              type="button"
              className="button button--secondary price-log__more"
              onClick={() => setVisible((n) => n + PAGE)}
            >
              {texts.priceLog.more(data.entries.length - visible)}
            </button>
          )}
        </>
      )}
    </section>
  );
}

function LogRow({ entry, latest }: { entry: PriceLogEntry; latest: boolean }) {
  const [open, setOpen] = useState(false);
  const rowClass = [
    "price-log__row",
    latest ? "price-log__row--latest" : "",
    entry.outcome === "publicada" || entry.outcome === "sin cambios"
      ? ""
      : "price-log__row--rejected",
    entry.outcome === "sin cambios" ? "price-log__row--unchanged" : "",
  ].join(" ");
  return (
    <li className={rowClass}>
      <div className="price-log__main">
        <div>
          <strong>{formatDateTime(new Date(entry.quoted_at))}</strong>
          <small>{agreement(entry)}</small>
        </div>
        <p className="price-log__exchange">
          {entry.published || entry.median_cents === null
            ? texts.priceLog.exchangeLine(
                entry.price_soles !== null ? formatSoles(entry.price_soles) : "—",
                entry.cents_per_pound !== null ? formatCents(entry.cents_per_pound) : "—",
              )
            : texts.priceLog.medianLine(formatCents(entry.median_cents))}
          {entry.exchange_rate !== null &&
            ` · ${texts.priceLog.rate(formatNumber(entry.exchange_rate, 3))}`}
          {entry.exchange_source && (
            <>
              {" ("}
              <SourceName name={entry.exchange_source} />
              {")"}
            </>
          )}
        </p>
        <LocalPrices entry={entry} />
      </div>
      <button
        type="button"
        className="price-log__toggle"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {open ? texts.priceLog.hideSources : texts.priceLog.showSources(entry.readings.length)}
      </button>
      {open && <SourceReadings readings={entry.readings} medianCents={entry.median_cents} />}
    </li>
  );
}

/** «2 de 4 webs coinciden», o por qué no se publicó (con el motivo real que guardó la API). */
function agreement(entry: PriceLogEntry): string {
  if (entry.outcome === "sin cambios") return texts.priceLog.unchanged;
  if (entry.outcome === "sin datos") return texts.priceLog.noData;
  if (!entry.published) {
    return entry.detail
      ? texts.priceLog.notPublishedBecause(entry.detail)
      : texts.priceLog.notPublished;
  }
  if (entry.readings.length === 0) return entry.sources.join(", ");
  const used = entry.readings.filter((reading) => reading.status === "usada").length;
  return texts.priceLog.agreement(used, entry.readings.length);
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span className="stat__label">{label}</span>
      <span className="stat__value">{value}</span>
    </div>
  );
}

/** Estimado en Jaén de los tres tipos de café (la bolsa es una sola para todos). */
function LocalPrices({ entry }: { entry: PriceLogEntry }) {
  if (!entry.published) return null;
  const known = TYPES.filter((type) => entry.local_soles[type] !== undefined);
  if (known.length === 0) {
    return <p className="price-log__locals muted">{texts.priceLog.noLocal}</p>;
  }
  return (
    <p className="price-log__locals">
      <span>{texts.priceLog.inJaen}</span>
      {known.map((type) => (
        <span key={type} className="price-log__local-chip">
          {texts.local.coffeeTypes[type]}{" "}
          <strong>{formatSoles(entry.local_soles[type] ?? 0)}</strong>
        </span>
      ))}
    </p>
  );
}
