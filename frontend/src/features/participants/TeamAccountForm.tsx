import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import { PasswordInput } from "../../shared/components/PasswordInput";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

const EMPTY = { name: "", phone: "", password: "" };

/**
 * Un administrador crea otra cuenta del equipo con su celular y contraseña. Queda activa al
 * instante (sin código ni verificación): se le entregan los datos en persona.
 */
export function TeamAccountForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState<ApiError | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const update = (field: keyof typeof EMPTY) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [field]: event.target.value }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setDone(null);
    try {
      await api.post("/admin/team", form);
      setDone(texts.participants.teamCreated(form.name || form.phone, form.phone));
      setForm(EMPTY);
      onCreated();
    } catch (caught) {
      setError(caught as ApiError);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="form card" onSubmit={submit}>
      <h3 className="form__title">{texts.participants.newTeamTitle}</h3>
      <p className="muted">{texts.participants.newTeamIntro}</p>
      <label>
        {texts.auth.name}
        <input maxLength={80} value={form.name} onChange={update("name")} required />
      </label>
      <label>
        {texts.auth.phone}
        <input
          inputMode="numeric"
          maxLength={9}
          value={form.phone}
          onChange={update("phone")}
          required
        />
      </label>
      <label>
        {texts.auth.password}
        <PasswordInput
          autoComplete="new-password"
          minLength={8}
          value={form.password}
          onChange={update("password")}
          required
        />
      </label>
      <StatusMessage error={error} />
      {done && !error && <p className="banner">{done}</p>}
      <button className="button" disabled={busy}>
        {texts.participants.createTeam}
      </button>
    </form>
  );
}
