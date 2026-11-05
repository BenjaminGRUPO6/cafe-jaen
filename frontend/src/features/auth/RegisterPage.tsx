import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../../shared/api/client";
import { useAuth } from "../../shared/auth/AuthContext";
import { Brand } from "../../shared/components/Brand";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { PasswordInput } from "../../shared/components/PasswordInput";
import { texts } from "../../shared/texts/es";
import { verifyPath } from "./VerifyPage";

/** HU01: registro con código de invitación, correo y consentimiento informado. */
export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    invitation_code: "",
    name: "",
    phone: "",
    email: "",
    password: "",
  });
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const update = (field: keyof typeof form) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [field]: event.target.value }));

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const pending = await register({ ...form, consent_accepted: consent });
      // Sin sesión todavía: primero se confirma el código que llegó al correo
      navigate(verifyPath(pending.phone), { state: pending });
    } catch (caught) {
      setError(caught as ApiError);
    }
  };

  return (
    <main className="content auth">
      <div className="auth__hero">
        <Brand />
        <img
          className="auth__cover"
          src="/ilustraciones/portada-cafe-jaen.svg"
          alt={texts.auth.coverAlt}
          width={1200}
          height={480}
        />
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
          {texts.auth.name}
          <input
            autoComplete="name"
            maxLength={80}
            value={form.name}
            onChange={update("name")}
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
          {texts.auth.email}
          <input
            type="email"
            inputMode="email"
            autoComplete="email"
            value={form.email}
            onChange={update("email")}
          />
          <small className="muted">{texts.auth.emailHint}</small>
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
