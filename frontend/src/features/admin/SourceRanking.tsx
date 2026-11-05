import { formatNumber } from "../../shared/format";
import { SourceName } from "../../shared/components/SourceName";
import { texts } from "../../shared/texts/es";
import type { SourceScore } from "./priceLog";

/**
 * Evaluación de las webs de la bolsa en el día elegido: cuánto respondieron, cuánto coincidieron
 * con las demás y qué tan al día estaban. La primera es la mejor fuente.
 */
export function SourceRanking({ ranking }: { ranking: SourceScore[] }) {
  if (ranking.length === 0) return null;
  const t = texts.priceLog.ranking;
  return (
    <section className="card ranking" aria-labelledby="ranking-title">
      <h2 id="ranking-title">{t.title}</h2>
      <p className="muted">{t.intro}</p>
      <ol className="ranking__list">
        {ranking.map((score, index) => (
          <li
            key={score.source}
            className={index === 0 ? "ranking__item ranking__item--best" : "ranking__item"}
          >
            <div className="ranking__top">
              <strong>
                <SourceName name={score.source} />
              </strong>
              {index === 0 && score.score > 0 && <span className="ranking__badge">{t.best}</span>}
              <span className="ranking__score">{t.score(formatNumber(score.score, 0))}</span>
            </div>
            <div className="ranking__bar" aria-hidden="true">
              <span style={{ width: `${Math.min(100, Math.max(0, score.score))}%` }} />
            </div>
            <p className="ranking__detail">{describe(score)}</p>
          </li>
        ))}
      </ol>
      <p className="ranking__formula">{t.formula}</p>
    </section>
  );
}

/** «Respondió 3 de 3 · coincidió 3 de 3 · 10 min de retraso · desvío medio 0,01 %». */
function describe(score: SourceScore): string {
  const t = texts.priceLog.ranking;
  const parts = [t.answered(score.answered, score.consultations)];
  if (score.answered > 0) {
    parts.push(t.used(score.used, score.answered));
    parts.push(
      score.avg_delay_minutes !== null
        ? t.delay(formatNumber(score.avg_delay_minutes, 0))
        : t.noDelay,
    );
  }
  if (score.avg_deviation_pct !== null) {
    parts.push(t.deviation(formatNumber(score.avg_deviation_pct, 2)));
  }
  return parts.join(" · ");
}
