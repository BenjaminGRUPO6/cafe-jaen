import { useEffect } from "react";
import { Link } from "react-router-dom";
import type { LivePrice } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import {
  formatCents,
  formatDate,
  formatPercent,
  formatSoles,
  formatTime,
} from "../../shared/format";
import { useLivePrice } from "../../shared/hooks/useLivePrice";
import { useOnlineStatus } from "../../shared/hooks/useOnlineStatus";
import { texts } from "../../shared/texts/es";
import { loadLastPrice, saveLastPrice } from "./lastPriceCache";
import { LocalEstimateCard } from "./LocalEstimateCard";

/** HU03: precio mundial en vivo, como una pantalla de bolsa; se actualiza solo. */
export function LivePricePage() {
  const { price: live, error } = useLivePrice();

  useEffect(() => {
    if (live) saveLastPrice(live);
  }, [live]);

  // Sin conexión: se muestra el último precio guardado, avisando de cuándo es (HU09)
  const online = useOnlineStatus();
  const cached = !online || (error && !live) ? loadLastPrice() : null;
  const price = live ?? cached?.price;

  return (
    <section>
      <h1>{texts.live.title}</h1>
      {cached && (
        <p className="banner" role="status">
          {texts.common.offline(
            `${formatTime(cached.price.quoted_at)} del ${formatDate(cached.price.date)}`,
          )}
        </p>
      )}
      {price ? (
        <>
          <PriceBoard price={price} live={Boolean(live) && online && !error} />
          <LocalEstimateCard estimates={price.local_estimates ?? []} />
          <Link to="/vender" className="button button--block">
            {texts.live.askDecision}
          </Link>
        </>
      ) : (
        <StatusMessage loading={!error} error={error} />
      )}
    </section>
  );
}

function PriceBoard({ price, live }: { price: LivePrice; live: boolean }) {
  const change = price.change_soles;
  return (
    <article className="card" aria-live="polite">
      <div className="board__top">
        <span className="muted">{texts.live.market}</span>
        {live && price.market_open && <span className="live-badge">{texts.live.liveBadge}</span>}
      </div>
      <p className="price">{formatSoles(price.price_soles)}</p>
      <p>
        {texts.common.perQuintal} · {formatCents(price.cents_per_pound)}
      </p>
      {change !== null && price.change_pct !== null && (
        <p className={change >= 0 ? "up" : "down"}>
          {change >= 0 ? "▲ " + texts.live.up : "▼ " + texts.live.down}{" "}
          {formatSoles(Math.abs(change))} ({formatPercent(Math.abs(price.change_pct))}){" "}
          {texts.live.sincePreviousClose}
        </p>
      )}
      <p className="muted">
        {texts.live.quotedAt(formatTime(price.quoted_at), formatDate(price.date))}
      </p>
      <p className={price.market_open ? "market-state market-state--open" : "market-state"}>
        {price.market_open ? texts.live.open : texts.live.closed}
      </p>
      {price.stale && <p className="banner">{texts.live.stale}</p>}
      <p className="muted">
        {texts.common.source}: {price.sources.join(", ")}. {texts.live.delayNote}
      </p>
    </article>
  );
}
