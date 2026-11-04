import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../../shared/api/client";
import { useAuth } from "../../shared/auth/AuthContext";
import { Brand } from "../../shared/components/Brand";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

/** HU01: registro con código de invitación y consentimiento informado. */
export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ invitation_code: "", phone: "", password: "" });
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const update = (field: keyof typeof form) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [field]: event.target.value }));

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await register({ ...form, consent_accepted: consent });
      navigate("/");
    } catch (caught) {
      setError(caught as ApiError);
    }
  };

  return (
    <main className="content auth">
      <div className="auth__hero tile tile--grano">
        <Brand />
        <p className="auth__tagline">{texts.auth.tagline}</p>
      </div>
      <h1>{texts.auth.registerTitle}</h1>
      <form className="form card" onSubmit={onSubmit}>
        <label>
          {texts.auth.invitationCode}
          <input
            value={form.invitation_code}
            onChange={update("invitation_code")}
            autoCapitalize="characters"
            required
          />
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
          <input
            type="password"
            minLength={8}
            value={form.password}
            onChange={update("password")}
            required
          />
        </label>
        <fieldset className="card">
          <legend>{texts.auth.consentTitle}</legend>
          <p className="muted">{texts.auth.consentText}</p>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
            />
            {texts.auth.consentAccept}
          </label>
        </fieldset>
        <StatusMessage error={error} />
        {/* Sin aceptar el consentimiento no se puede continuar (PA-01-3) */}
        <button className="button" disabled={!consent}>
          {texts.auth.register}
        </button>
      </form>
      <Link to="/ingresar">{texts.auth.goToLogin}</Link>
    </main>
  );
}
