import { motion } from "framer-motion";
import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { LivePrice, PriceHistory } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import {
  formatCents,
  formatDate,
  formatPercent,
  formatSoles,
  formatTime,
} from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useLivePrice } from "../../shared/hooks/useLivePrice";
import { useOnlineStatus } from "../../shared/hooks/useOnlineStatus";
import { DecisionIcon, ForecastIcon } from "../../shared/motion/icons";
import { RevealGroup, RevealItem } from "../../shared/motion/Reveal";
import { Sparkline } from "../../shared/motion/Sparkline";
import { Ticker } from "../../shared/motion/Ticker";
import { texts } from "../../shared/texts/es";
import { loadLastPrice, saveLastPrice } from "./lastPriceCache";
import { LocalEstimateCard } from "./LocalEstimateCard";

/** HU03: precio mundial en vivo, como una pantalla de bolsa; se actualiza solo. */
export function LivePricePage() {
  const { price: live, error } = useLivePrice();
  const { data: today } = useApi<PriceHistory>("/prices/history?period=today");

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
        <p className="banner banner--warning" role="status">
          {texts.common.offline(
            `${formatTime(cached.price.quoted_at)} del ${formatDate(cached.price.date)}`,
          )}
        </p>
      )}
      {price ? (
        <RevealGroup className="bento">
          <RevealItem className="tile tile--grano">
            <PriceBoard
              price={price}
              live={Boolean(live) && online && !error}
              trend={today?.points.map((point) => point.price_soles) ?? []}
            />
          </RevealItem>
          <RevealItem className="tile tile--brote">
            <LocalEstimateCard estimates={price.local_estimates ?? []} />
          </RevealItem>
          <RevealItem className="tile tile--espresso tile--half">
            <ActionTile
              to="/vender"
              icon={<DecisionIcon />}
              title={texts.live.askDecision}
              hint={texts.live.decisionHint}
            />
          </RevealItem>
          <RevealItem className="tile tile--half">
            <ActionTile
              to="/pronostico"
              icon={<ForecastIcon />}
              title={texts.live.forecastTile}
              hint={texts.live.forecastHint}
            />
          </RevealItem>
        </RevealGroup>
      ) : (
        <StatusMessage loading={!error} error={error} />
      )}
      {price && (
        <p className="footnote">
          {texts.common.source}: {price.sources.join(", ")}.{" "}
          {texts.live.quotedAt(formatTime(price.quoted_at), formatDate(price.date))}.{" "}
          {texts.live.delayNote}
        </p>
      )}
    </section>
  );
}

function PriceBoard({ price, live, trend }: { price: LivePrice; live: boolean; trend: number[] }) {
  const change = price.change_soles;
  // Al llegar un precio nuevo, el número se ilumina un instante (más claro si subió, rojizo si bajó)
  const [previous, setPrevious] = useState(price.price_soles);
  const [flash, setFlash] = useState<{ id: number; up: boolean } | null>(null);
  if (previous !== price.price_soles) {
    setFlash({ id: (flash?.id ?? 0) + 1, up: price.price_soles > previous });
    setPrevious(price.price_soles);
  }

  return (
    <article aria-live="polite">
      <div className="tile__top">
        <span className="tile__label">{texts.live.market}</span>
        {live && price.market_open && (
          <span className="pill">
            <motion.span
              className="pill__dot"
              animate={{ opacity: [1, 0.2, 1] }}
              transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
            />
            {texts.live.liveBadge}
          </span>
        )}
      </div>
      <div className="price-wrap">
        {flash && (
          <motion.span
            key={flash.id}
            className={`price-flash ${flash.up ? "price-flash--up" : "price-flash--down"}`}
            initial={{ opacity: 1 }}
            animate={{ opacity: 0 }}
            transition={{ duration: 1.4, ease: "easeOut" }}
          />
        )}
        <p className="price">
          <Ticker value={formatSoles(price.price_soles)} />
        </p>
      </div>
      <p className="price-unit">
        {texts.common.perQuintal} · {formatCents(price.cents_per_pound)}
      </p>
      <div className="price-row">
        {change !== null && price.change_pct !== null && (
          <p className={`pill pill--wrap ${change >= 0 ? "pill--up" : "pill--down"}`}>
            <span aria-hidden="true">{change >= 0 ? "▲" : "▼"}</span>
            <span>
              {change >= 0 ? texts.live.up : texts.live.down} {formatSoles(Math.abs(change))} (
              {formatPercent(Math.abs(price.change_pct))}) {texts.live.sincePreviousClose}
            </span>
          </p>
        )}
        <p className={`pill pill--quiet ${price.market_open ? "pill--open" : ""}`}>
          <span className="pill__dot" aria-hidden="true" />
          {price.market_open ? texts.live.openShort : texts.live.closedShort}
        </p>
      </div>
      {price.stale && <p className="banner">{texts.live.stale}</p>}
      <Sparkline values={trend} />
    </article>
  );
}

function ActionTile({
  to,
  icon,
  title,
  hint,
}: {
  to: string;
  icon: ReactNode;
  title: string;
  hint: string;
}) {
  return (
    <motion.div whileTap={{ scale: 0.97 }}>
      <Link to={to} className="tile-link">
        <span className="tile-link__icon">{icon}</span>
        <span>
          <p className="tile-link__title">{title}</p>
          <p className="tile-link__hint">{hint}</p>
        </span>
      </Link>
    </motion.div>
  );
}
