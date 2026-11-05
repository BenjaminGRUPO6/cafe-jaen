import { motion } from "framer-motion";
import type { CoffeeType, Cooperative, LocalPriceObservation } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDateTime, formatPercent, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { ExternalIcon } from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";
import { latestByCooperative } from "./latestByCooperative";

/** Vista «Por cooperativa»: lo último que pagó cada una por el tipo de café elegido. */
export function CooperativePrices({ coffeeType }: { coffeeType: CoffeeType }) {
  const prices = useApi<{ observations: LocalPriceObservation[] }>("/prices/local");
  const catalog = useApi<{ cooperatives: Cooperative[] }>("/cooperatives");
  if (!prices.data) return <StatusMessage loading={!prices.error} error={prices.error} />;

  const rows = latestByCooperative(prices.data.observations, coffeeType);
  const websites = new Map(catalog.data?.cooperatives.map((c) => [c.name, c.website]) ?? []);
  if (rows.length === 0) {
    return <p className="muted">{texts.local.coopsEmpty(texts.local.coffeeTypes[coffeeType])}</p>;
  }
  return (
    <>
      <ul className="coop-prices">
        {rows.map((row, index) => (
          <motion.li
            key={row.cooperative}
            className="coop-prices__row"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className="coop-prices__name">
              <strong>{row.cooperative}</strong>
              <small>
                {texts.local.paid(formatDateTime(new Date(row.observed_at)))} ·{" "}
                {texts.local.ofExchange(formatPercent(row.ratio_pct))}
              </small>
            </div>
            <div className="coop-prices__value">
              <strong>{formatSoles(row.paid_soles)}</strong>
              {websites.get(row.cooperative) && (
                <a
                  href={websites.get(row.cooperative) ?? undefined}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="coop-prices__web"
                >
                  {texts.local.website} <ExternalIcon />
                </a>
              )}
            </div>
          </motion.li>
        ))}
      </ul>
      <p className="muted">{texts.local.coopsNote}</p>
    </>
  );
}
