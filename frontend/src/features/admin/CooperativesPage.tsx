import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import type { Cooperative } from "../../shared/api/types";
import { ConfirmButton } from "../../shared/components/ConfirmButton";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { useApi } from "../../shared/hooks/useApi";
import { EditIcon, ExternalIcon, TrashIcon } from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "./AdminTabs";

interface CooperativeForm {
  name: string;
  location: string;
  website: string;
  active: boolean;
}

const EMPTY: CooperativeForm = { name: "", location: "Jaén", website: "", active: true };

/** Catálogo de cooperativas: agregar, editar, archivar o quitar (solo el equipo). */
export function CooperativesPage() {
  const { data, error, loading, reload } = useApi<{ cooperatives: Cooperative[] }>(
    "/admin/cooperatives",
  );
  const [message, setMessage] = useState<string | null>(null);

  return (
    <section>
      <AdminTabs />
      <h1>{texts.cooperatives.title}</h1>
      <p className="muted">{texts.cooperatives.intro}</p>
      <CooperativeEditor
        initial={EMPTY}
        submitLabel={texts.cooperatives.add}
        onSubmit={async (form) => {
          const created = await api.post<Cooperative>("/admin/cooperatives", toBody(form));
          setMessage(texts.cooperatives.created(created.name));
          reload();
        }}
      />
      {message && (
        <p className="up" role="status">
          {message}
        </p>
      )}
      <StatusMessage loading={loading} error={error} onRetry={reload} />
      {data && (
        <ul className="card observations">
          {data.cooperatives.map((c) => (
            <CooperativeRow
              key={c.id}
              cooperative={c}
              onChanged={(text) => {
                setMessage(text);
                reload();
              }}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function CooperativeRow({
  cooperative: c,
  onChanged,
}: {
  cooperative: Cooperative;
  onChanged: (message: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const remove = async () => {
    try {
      const { result } = await api.delete<{ result: "deleted" | "archived" }>(
        `/admin/cooperatives/${c.id}`,
      );
      onChanged(texts.cooperatives.removed[result]);
    } catch (caught) {
      setError(caught as ApiError);
    }
  };

  return (
    <li className={`observation ${c.active ? "" : "observation--archived"}`}>
      <div className="observation__head">
        <span>
          <strong>{c.name}</strong>
          {!c.active && <span className="pill pill--quiet">{texts.cooperatives.archived}</span>}
        </span>
        <span className="observation__actions">
          <button
            type="button"
            className="icon-button"
            aria-label={texts.cooperatives.edit}
            onClick={() => setEditing((value) => !value)}
          >
            <EditIcon />
          </button>
          <ConfirmButton label={texts.cooperatives.remove} onConfirm={() => void remove()}>
            <TrashIcon />
          </ConfirmButton>
        </span>
      </div>
      <span className="muted">
        {c.location}
        {c.website && (
          <>
            {" · "}
            <a href={c.website} target="_blank" rel="noopener noreferrer" className="inline-link">
              {c.website.replace(/^https?:\/\//, "")} <ExternalIcon />
            </a>
          </>
        )}
      </span>
      {editing && (
        <CooperativeEditor
          initial={{
            name: c.name,
            location: c.location,
            website: c.website ?? "",
            active: c.active,
          }}
          submitLabel={texts.cooperatives.save}
          withActive
          onSubmit={async (form) => {
            await api.put(`/admin/cooperatives/${c.id}`, toBody(form));
            setEditing(false);
            onChanged(texts.cooperatives.updated);
          }}
        />
      )}
      <StatusMessage error={error} />
    </li>
  );
}

function CooperativeEditor({
  initial,
  submitLabel,
  withActive = false,
  onSubmit,
}: {
  initial: CooperativeForm;
  submitLabel: string;
  withActive?: boolean;
  onSubmit: (form: CooperativeForm) => Promise<void>;
}) {
  const [form, setForm] = useState(initial);
  const [error, setError] = useState<ApiError | null>(null);
  const [saving, setSaving] = useState(false);
  const set = (changes: Partial<CooperativeForm>) => setForm((f) => ({ ...f, ...changes }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSubmit(form);
      if (!withActive) setForm(EMPTY); // al agregar se limpia el formulario
    } catch (caught) {
      setError(caught as ApiError);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="form card" onSubmit={submit}>
      <label>
        {texts.cooperatives.name}
        <input
          value={form.name}
          onChange={(e) => set({ name: e.target.value })}
          required
          minLength={2}
          maxLength={80}
        />
      </label>
      <label>
        {texts.cooperatives.location}
        <input
          value={form.location}
          onChange={(e) => set({ location: e.target.value })}
          maxLength={80}
        />
      </label>
      <label>
        {texts.cooperatives.website}
        <input
          value={form.website}
          onChange={(e) => set({ website: e.target.value })}
          type="url"
          placeholder="https://"
          maxLength={200}
        />
      </label>
      {withActive && (
        <label className="check">
          <input
            type="checkbox"
            checked={form.active}
            onChange={(e) => set({ active: e.target.checked })}
          />
          {texts.cooperatives.active}
        </label>
      )}
      <button className="button" disabled={saving}>
        {submitLabel}
      </button>
      <StatusMessage error={error} />
    </form>
  );
}

function toBody(form: CooperativeForm) {
  return { ...form, website: form.website.trim() || null };
}
