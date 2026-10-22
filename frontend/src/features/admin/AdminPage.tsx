import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import type { CoffeeType, LocalPriceObservation } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatPercent, formatSoles, formatTime } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { texts } from "../../shared/texts/es";

const TYPES: CoffeeType[] = ["convencional", "organico", "especial"];

/** HU12: el equipo anota cuánto paga cada cooperativa; la app guarda la bolsa del momento. */
export function AdminPage() {
  const { data, error, loading, reload } = useApi<{ observations: LocalPriceObservation[] }>(
    "/admin/local-prices",
  );
  const [cooperative, setCooperative] = useState("");
  const [coffeeType, setCoffeeType] = useState<CoffeeType>("convencional");
  const [paid, setPaid] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<ApiError | null>(null);
  const [saving, setSaving] = useState(false);
  const known = [...new Set(data?.observations.map((o) => o.cooperative) ?? [])];

  const save = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setSaveError(null);
    setMessage(null);
    try {
      const saved = await api.post<LocalPriceObservation>("/admin/local-prices", {
        cooperative,
        coffee_type: coffeeType,
        paid_soles: Number(paid.replace(",", ".")),
      });
      setMessage(texts.admin.saved(formatPercent(saved.ratio_pct)));
      setPaid("");
      reload();
    } catch (caught) {
      setSaveError(caught as ApiError);
    } finally {
      setSaving(false);
    }
  };

  return (
    <section>
      <h1>{texts.admin.title}</h1>
      <p className="muted">{texts.admin.intro}</p>
      <form className="form card" onSubmit={save}>
        <label>
          {texts.admin.cooperative}
          <input
            value={cooperative}
            onChange={(e) => setCooperative(e.target.value)}
            list="cooperatives"
            required
            maxLength={80}
          />
          <datalist id="cooperatives">
            {known.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
        </label>
        <label>
          {texts.admin.coffeeType}
          <select value={coffeeType} onChange={(e) => setCoffeeType(e.target.value as CoffeeType)}>
            {TYPES.map((type) => (
              <option key={type} value={type}>
                {texts.local.coffeeTypes[type]}
              </option>
            ))}
          </select>
        </label>
        <label>
          {texts.admin.paid}
          <input
            value={paid}
            onChange={(e) => setPaid(e.target.value)}
            inputMode="decimal"
            required
          />
        </label>
        <button className="button" disabled={saving}>
          {texts.admin.save}
        </button>
        {message && (
          <p className="up" role="status">
            {message}
          </p>
        )}
        <StatusMessage error={saveError} />
      </form>

      <h2 className="card__title">{texts.admin.recent}</h2>
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <ul className="card observations">
          {data.observations.map((o) => (
            <li key={o.observed_at + o.cooperative}>
              <strong>{o.cooperative}</strong> · {texts.local.coffeeTypes[o.coffee_type]}
              <br />
              <span className="muted">
                {o.observed_at.slice(8, 10)}/{o.observed_at.slice(5, 7)} {formatTime(o.observed_at)}{" "}
                · {texts.admin.paidShort} {formatSoles(o.paid_soles)} · {texts.admin.exchange}{" "}
                {formatSoles(o.exchange_soles)} · <strong>{formatPercent(o.ratio_pct)}</strong>
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
