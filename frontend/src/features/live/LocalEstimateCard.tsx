import { useState } from "react";
import type { LocalEstimate } from "../../shared/api/types";
import { InfoNote } from "../../shared/components/InfoNote";
import { formatDate, formatPercent, formatSoles } from "../../shared/format";
import { useCoffeeType } from "../../shared/hooks/useCoffeeType";
import { Segmented } from "../../shared/motion/Segmented";
import { Sparkline } from "../../shared/motion/Sparkline";
import { Ticker } from "../../shared/motion/Ticker";
import { texts } from "../../shared/texts/es";
import { CooperativePrices } from "./CooperativePrices";

type View = "general" | "cooperatives";

/**
 * HU12: lo que se paga en Jaén. «General» es el estimado (bolsa × mediana de los porcentajes);
 * «Por cooperativa» muestra lo último que pagó cada una. El tipo de café elegido se recuerda.
 */
export function LocalEstimateCard({
  estimates,
  exchangeSoles,
  todayExchange,
}: {
  estimates: LocalEstimate[];
  exchangeSoles: number;
  todayExchange: number[];
}) {
  const [chosen, choose] = useCoffeeType();
  const [view, setView] = useState<View>("general");
  const estimate = estimates.find((e) => e.coffee_type === chosen);

  return (
    <article>
      <h2 className="tile__title">{texts.local.title}</h2>
      <Segmented
        label={texts.local.title}
        value={view}
        onChange={setView}
        options={[
          { value: "general", label: texts.local.general },
          { value: "cooperatives", label: texts.local.byCooperative },
        ]}
      />
      <Segmented
        label={texts.admin.coffeeType}
        value={chosen}
        onChange={choose}
        options={(["convencional", "organico", "especial"] as const).map((type) => ({
          value: type,
          label: texts.local.coffeeTypes[type],
        }))}
      />
      {view === "cooperatives" ? (
        <CooperativePrices coffeeType={chosen} />
      ) : estimate ? (
        <GeneralEstimate
          estimate={estimate}
          exchangeSoles={exchangeSoles}
          todayExchange={todayExchange}
        />
      ) : (
        <p className="muted">{texts.local.empty}</p>
      )}
    </article>
  );
}

function GeneralEstimate({
  estimate,
  exchangeSoles,
  todayExchange,
}: {
  estimate: LocalEstimate;
  exchangeSoles: number;
  todayExchange: number[];
}) {
  const pct = formatPercent(estimate.ratio_pct);
  // El estimado en Jaén de hoy, minuto a minuto: la bolsa de cada minuto × el mismo porcentaje
  const trend = localTrend(todayExchange, estimate.ratio_pct);
  return (
    <>
      <p className="price price--secondary">
        <Ticker value={`≈ ${formatSoles(estimate.estimated_soles)}`} />
      </p>
      <p className="price-unit">
        {texts.local.unit} · {texts.local.ratio(pct)}
      </p>
      <Sparkline values={trend} />
      {trend.length >= 2 && <p className="sparkline__caption">{texts.local.trendCaption}</p>}
      {estimate.few_data && <p className="banner">{texts.local.fewData}</p>}
      {(estimate.synthetic_observations ?? 0) > 0 && (
        <p className="synthetic-note" role="note">
          {texts.local.synthetic(estimate.synthetic_observations ?? 0, estimate.observations)}
        </p>
      )}
      <p className="muted">
        {texts.local.basis(
          estimate.observations,
          formatDate(estimate.first_day),
          formatDate(estimate.last_day),
        )}{" "}
        {texts.local.note}
      </p>
      <InfoNote>
        <ol>
          {texts.info
            .estimateSteps(
              estimate.observations,
              pct,
              formatSoles(exchangeSoles),
              formatSoles(estimate.estimated_soles),
            )
            .map((step) => (
              <li key={step}>{step}</li>
            ))}
        </ol>
      </InfoNote>
    </>
  );
}

/** Precio en Jaén de cada minuto de hoy (se descarta lo que no sea un número válido). */
export function localTrend(exchange: number[], ratioPct: number): number[] {
  return exchange
    .filter((value) => Number.isFinite(value))
    .map((value) => Math.round(value * ratioPct) / 100);
}
