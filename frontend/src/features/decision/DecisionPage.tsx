import { motion } from "framer-motion";
import type { JSX } from "react";
import type { SellingAdvice, Verdict } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDate, formatPercent, formatSoles } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { NoSignalIcon, RefreshIcon, SellIcon, WaitIcon } from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";

// Cada veredicto tiene su color y su ícono (verde-lima: vender, azul: esperar)
const LOOK: Record<Verdict, { tile: string; Icon: () => JSX.Element }> = {
  "Vender ahora": { tile: "tile tile--brote", Icon: SellIcon },
  Esperar: { tile: "tile tile--cielo", Icon: WaitIcon },
  "Sin señal clara": { tile: "tile", Icon: NoSignalIcon },
  "Sin datos suficientes": { tile: "tile", Icon: NoSignalIcon },
};

/** HU05: recomendación explicada de vender ahora o esperar (la decisión es del caficultor). */
export function DecisionPage() {
  const { data, error, loading, reload } = useApi<SellingAdvice>("/decision/today");
  const look = data ? LOOK[data.verdict] : null;

  return (
    <section>
      <h1>{texts.decision.title}</h1>
      <p className="muted">{texts.decision.basedOn}</p>
      <StatusMessage loading={loading && !data} error={error} onRetry={reload} />
      {data && look && (
        // El veredicto aparece con un pequeño impulso cada vez que se calcula
        <motion.article
          key={data.verdict + data.reason}
          className={look.tile}
          initial={{ opacity: 0, scale: 0.94, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 280, damping: 22 }}
        >
          <motion.span
            className="verdict-icon"
            initial={{ rotate: -90, scale: 0.4 }}
            animate={{ rotate: 0, scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 16, delay: 0.1 }}
          >
            <look.Icon />
          </motion.span>
          <p className="verdict">{data.verdict}</p>
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
          <motion.button
            className="button button--block"
            onClick={reload}
            disabled={loading}
            whileTap={{ scale: 0.97 }}
          >
            <motion.span
              animate={loading ? { rotate: 360 } : { rotate: 0 }}
              transition={loading ? { repeat: Infinity, duration: 0.9, ease: "linear" } : {}}
              style={{ display: "inline-flex" }}
            >
              <RefreshIcon />
            </motion.span>
            {texts.decision.refresh}
          </motion.button>
        </motion.article>
      )}
    </section>
  );
}
