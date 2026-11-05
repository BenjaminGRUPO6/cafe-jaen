import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import { ConfirmButton } from "../../shared/components/ConfirmButton";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDateTime } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { TrashIcon } from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "./AdminTabs";

interface InvitationCode {
  code: string;
  used: boolean;
  used_at: string | null;
}

const MAX_PER_REQUEST = 50; // el mismo tope que valida el backend

/** El equipo genera los códigos del GE desde la app y borra los que no se entregaron. */
export function CodesPage() {
  const { data, error, loading, reload } = useApi<{ codes: InvitationCode[] }>(
    "/admin/invitation-codes",
  );
  const [count, setCount] = useState("10");
  const [created, setCreated] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const [actionError, setActionError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);
  const free = data?.codes.filter((c) => !c.used) ?? [];
  const used = data?.codes.filter((c) => c.used) ?? [];

  const generate = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setActionError(null);
    setCopied(false);
    try {
      const body = await api.post<{ codes: string[] }>("/admin/invitation-codes", {
        count: Number(count),
      });
      setCreated(body.codes);
      reload();
    } catch (caught) {
      setActionError(caught as ApiError);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (code: string) => {
    setActionError(null);
    try {
      await api.delete(`/admin/invitation-codes/${code}`);
      setCreated((list) => list.filter((c) => c !== code));
      reload();
    } catch (caught) {
      setActionError(caught as ApiError);
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(created.join("\n"));
      setCopied(true);
    } catch {
      setCopied(false); // sin permiso del navegador: el equipo puede copiarlos a mano
    }
  };

  return (
    <section>
      <AdminTabs />
      <h1>{texts.codes.title}</h1>
      <p className="muted">{texts.codes.intro}</p>
      <form className="form card inline-form" onSubmit={generate}>
        <label>
          {texts.codes.howMany}
          <input
            type="number"
            min={1}
            max={MAX_PER_REQUEST}
            value={count}
            onChange={(e) => setCount(e.target.value)}
            required
          />
        </label>
        <button className="button" disabled={busy}>
          {texts.codes.generate}
        </button>
      </form>
      {created.length > 0 && (
        <div className="card new-codes" role="status">
          <p>{texts.codes.generated(created.length)}</p>
          <p className="new-codes__list">{created.join("  ·  ")}</p>
          <button type="button" className="button button--secondary" onClick={() => void copy()}>
            {copied ? texts.codes.copied : texts.codes.copy}
          </button>
        </div>
      )}
      <StatusMessage error={actionError} />
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <>
          <div className="stats">
            <Stat label={texts.codes.free} value={String(free.length)} />
            <Stat label={texts.codes.used} value={String(used.length)} />
            <Stat label={texts.codes.total} value={String(data.codes.length)} />
          </div>
          <ul className="codes">
            {free.map((c) => (
              <li key={c.code} className="codes__item">
                <code>{c.code}</code>
                <ConfirmButton label={texts.codes.remove} onConfirm={() => void remove(c.code)}>
                  <TrashIcon />
                </ConfirmButton>
              </li>
            ))}
            {used.map((c) => (
              <li key={c.code} className="codes__item codes__item--used">
                <code>{c.code}</code>
                <small>
                  {c.used_at && texts.codes.usedOn(formatDateTime(new Date(c.used_at)))}
                </small>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span className="stat__label">{label}</span>
      <span className="stat__value">{value}</span>
    </div>
  );
}
