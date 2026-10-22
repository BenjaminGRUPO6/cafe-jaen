import { useState } from "react";
import type { CoffeeType, LocalEstimate } from "../../shared/api/types";
import { formatDate, formatPercent, formatSoles } from "../../shared/format";
import { readStored, writeStored } from "../../shared/storage";
import { texts } from "../../shared/texts/es";

const KEY = "cafe-jaen.coffee-type";

/** HU12: precio estimado en Jaén con filtro por tipo de café (se recuerda la última elección). */
export function LocalEstimateCard({ estimates }: { estimates: LocalEstimate[] }) {
  const [chosen, setChosen] = useState<CoffeeType>(
    () => (readStored(KEY) as CoffeeType | null) ?? "convencional",
  );
  if (estimates.length === 0) {
    return (
      <article className="card">
        <h2 className="card__title">{texts.local.title}</h2>
        <p className="muted">{texts.local.empty}</p>
      </article>
    );
  }
  const estimate = estimates.find((e) => e.coffee_type === chosen) ?? estimates[0];
  const choose = (type: CoffeeType) => {
    setChosen(type);
    writeStored(KEY, type);
  };

  return (
    <article className="card">
      <h2 className="card__title">{texts.local.title}</h2>
      {estimates.length > 1 && (
        <div className="segmented" role="group" aria-label={texts.local.title}>
          {estimates.map((e) => (
            <button
              key={e.coffee_type}
              className={`button ${e.coffee_type === estimate.coffee_type ? "" : "button--secondary"}`}
              onClick={() => choose(e.coffee_type)}
            >
              {texts.local.coffeeTypes[e.coffee_type]}
            </button>
          ))}
        </div>
      )}
      <p className="price price--secondary">≈ {formatSoles(estimate.estimated_soles)}</p>
      <p>
        {texts.common.perQuintal} · {texts.local.ratio(formatPercent(estimate.ratio_pct))} ·{" "}
        {texts.local.coffeeTypes[estimate.coffee_type]}
      </p>
      {estimate.few_data && <p className="banner">{texts.local.fewData}</p>}
      <p className="muted">
        {texts.local.basis(
          estimate.observations,
          formatDate(estimate.first_day),
          formatDate(estimate.last_day),
        )}{" "}
        {texts.local.note}
      </p>
    </article>
  );
}
