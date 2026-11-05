import { formatCents } from "../../shared/format";
import { texts } from "../../shared/texts/es";
import type { SourceReading } from "./priceLog";

/** Lo que marcó cada web en una consulta y si entró o no en el precio publicado. */
export function SourceReadings({
  readings,
  medianCents,
}: {
  readings: SourceReading[];
  medianCents: number | null;
}) {
  if (readings.length === 0) {
    return <p className="readings__empty">{texts.priceLog.noReadings}</p>;
  }
  return (
    <div className="readings">
      {medianCents !== null && (
        <p className="readings__median">{texts.priceLog.median(formatCents(medianCents))}</p>
      )}
      <ul className="readings__list">
        {readings.map((reading) => (
          <li key={reading.source} className={`reading reading--${statusClass(reading.status)}`}>
            <div className="reading__top">
              <strong>{reading.source}</strong>
              <span className="reading__status">{texts.priceLog.status[reading.status]}</span>
            </div>
            {reading.cents_per_pound !== null ? (
              <p className="reading__detail">
                {formatCents(reading.cents_per_pound)}
                {reading.deviation_pct !== null &&
                  ` · ${texts.priceLog.deviation(reading.deviation_pct)}`}
                {reading.quoted_at && ` · ${texts.priceLog.sourceTime(clock(reading.quoted_at))}`}
              </p>
            ) : (
              <p className="reading__detail">{reading.detail ?? texts.priceLog.noAnswer}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function statusClass(status: SourceReading["status"]): string {
  return status === "usada" ? "used" : status === "descartada" ? "discarded" : "failed";
}

// La API entrega la hora en UTC: se muestra en la hora local del equipo
function clock(isoDateTime: string): string {
  return new Date(isoDateTime).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" });
}
