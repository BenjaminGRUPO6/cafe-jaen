import type { SellingAdvice, Verdict } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDate, formatPercent, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { texts } from "../../shared/texts/es";

const STYLE: Record<Verdict, string> = {
  "Vender ahora": "verdict verdict--sell",
  Esperar: "verdict verdict--wait",
  "Sin señal clara": "verdict",
  "Sin datos suficientes": "verdict",
};

/** HU05: recomendación explicada de vender ahora o esperar (la decisión es del caficultor). */
export function DecisionPage() {
  const { data, error, loading, reload } = useApi<SellingAdvice>("/decision/today");

  return (
    <section>
      <h1>{texts.decision.title}</h1>
      <p className="muted">{texts.decision.basedOn}</p>
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <article className="card">
          <p className={STYLE[data.verdict]}>{data.verdict}</p>
          <p>{data.reason}</p>
          {data.target_date && data.target_soles !== null && (
            <p className="muted">
              {texts.decision.target(formatDate(data.target_date), formatSoles(data.target_soles))}
            </p>
          )}
          {data.hit_rate_pct !== null && (
            <p className="muted">{texts.decision.hitRate(formatPercent(data.hit_rate_pct))}</p>
          )}
          <p className="banner">{data.disclaimer}</p>
          <button className="button button--secondary button--block" onClick={reload}>
            {texts.decision.refresh}
          </button>
        </article>
      )}
    </section>
  );
}
