import { useState } from "react";
import { api, ApiError } from "../../shared/api/client";
import { useApi } from "../../shared/hooks/useApi";
import { texts } from "../../shared/texts/es";

interface SyntheticStatus {
  cooperatives: number;
  observations: number;
}

/**
 * Carga o borra precios SINTÉTICOS de cooperativas para la demostración. El precio de la bolsa
 * que los acompaña es el real; antes del experimento se borran con un toque.
 */
export function SyntheticDataCard({ onChanged }: { onChanged: () => void }) {
  const { data, reload } = useApi<SyntheticStatus>("/admin/synthetic-data");
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const loaded = (data?.observations ?? 0) > 0;

  const run = async (
    action: () => Promise<SyntheticStatus>,
    done: (s: SyntheticStatus) => string,
  ) => {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      setMessage(done(await action()));
      reload();
      onChanged();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : String(caught));
    } finally {
      setBusy(false);
      setConfirming(false);
    }
  };

  return (
    <section className="card synthetic" aria-labelledby="synthetic-title">
      <h2 id="synthetic-title" className="card__title">
        {texts.synthetic.title}
      </h2>
      <p className="muted">{texts.synthetic.intro}</p>
      {data && (
        <p className={`pill pill--wrap ${loaded ? "synthetic__on" : "pill--quiet"}`} role="status">
          {loaded
            ? texts.synthetic.loaded(data.cooperatives, data.observations)
            : texts.synthetic.none}
        </p>
      )}
      <div className="synthetic__actions">
        <button
          type="button"
          className="button"
          disabled={busy}
          onClick={() =>
            void run(
              () => api.post<SyntheticStatus>("/admin/synthetic-data", {}),
              (s) => texts.synthetic.done(s.cooperatives, s.observations),
            )
          }
        >
          {loaded ? texts.synthetic.reload : texts.synthetic.load}
        </button>
        {loaded && (
          <button
            type="button"
            className={`button button--secondary ${confirming ? "button--danger" : ""}`}
            disabled={busy}
            onClick={() =>
              confirming
                ? void run(
                    () => api.delete<SyntheticStatus>("/admin/synthetic-data"),
                    (s) => texts.synthetic.removed(s.observations),
                  )
                : setConfirming(true)
            }
          >
            {confirming ? texts.synthetic.confirmRemove : texts.synthetic.remove}
          </button>
        )}
      </div>
      {message && (
        <p className="up" role="status">
          {message}
        </p>
      )}
      {error && <p className="banner banner--error">{error}</p>}
    </section>
  );
}
