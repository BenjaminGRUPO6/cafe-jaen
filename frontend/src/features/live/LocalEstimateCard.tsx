import type { LocalEstimate } from "../../shared/api/types";
import { formatDate, formatPercent, formatSoles } from "../../shared/format";
import { useCoffeeType } from "../../shared/hooks/useCoffeeType";
import { Segmented } from "../../shared/motion/Segmented";
import { Ticker } from "../../shared/motion/Ticker";
import { texts } from "../../shared/texts/es";

/** HU12: precio estimado en Jaén con filtro por tipo de café (se recuerda la última elección). */
export function LocalEstimateCard({ estimates }: { estimates: LocalEstimate[] }) {
  const [chosen, choose] = useCoffeeType();
  if (estimates.length === 0) {
    return (
      <article>
        <h2 className="tile__title">{texts.local.title}</h2>
        <p className="muted">{texts.local.empty}</p>
      </article>
    );
  }
  const estimate = estimates.find((e) => e.coffee_type === chosen) ?? estimates[0];

  return (
    <article>
      <h2 className="tile__title">{texts.local.title}</h2>
      {estimates.length > 1 && (
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
      <p className="price price--secondary">
        <Ticker value={`≈ ${formatSoles(estimate.estimated_soles)}`} />
      </p>
      <p className="price-unit">
        {texts.local.unit} · {texts.local.ratio(formatPercent(estimate.ratio_pct))}
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
