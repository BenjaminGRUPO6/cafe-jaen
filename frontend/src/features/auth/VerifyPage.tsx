import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../../shared/api/client";
import type { PendingVerification } from "../../shared/api/types";
import { useAuth } from "../../shared/auth/AuthContext";
import { Brand } from "../../shared/components/Brand";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

const RESEND_SECONDS = 60; // el mismo tiempo que exige la API entre un código y otro

/** Ruta de la pantalla de verificación para un celular. */
export function verifyPath(phone: string): string {
  return `/verificar?telefono=${encodeURIComponent(phone)}`;
}

/**
 * Confirma la cuenta con el código de 6 dígitos que llegó al correo. Si el correo no llega,
 * el caficultor puede pedir el código al equipo (lo ve en «Participantes»).
 */
export function VerifyPage() {
  const { verify } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const pending = useLocation().state as PendingVerification | null;
  const phone = pending?.phone ?? params.get("telefono") ?? "";
  const [email, setEmail] = useState(pending?.email ?? null);
  const [emailSent, setEmailSent] = useState(pending?.email_sent ?? true);
  const [code, setCode] = useState("");
  const [error, setError] = useState<ApiError | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [wait, setWait] = useState(pending ? RESEND_SECONDS : 0);

  useEffect(() => {
    if (wait <= 0) return;
    const timer = window.setTimeout(() => setWait((s) => s - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [wait]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await verify(phone, code);
      navigate("/");
    } catch (caught) {
      setError(caught as ApiError);
    }
  };

  const resend = async () => {
    setError(null);
    try {
      const sent = await api.post<{ email: string | null; email_sent: boolean }>("/auth/resend", {
        phone,
      });
      setEmail(sent.email);
      setEmailSent(sent.email_sent);
      setNotice(texts.verify.resent);
      setWait(RESEND_SECONDS);
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
      <h1>{texts.verify.title}</h1>
      <form className="form card" onSubmit={onSubmit}>
        <p>
          {emailSent ? texts.verify.sentTo(email ?? texts.verify.yourEmail) : texts.verify.notSent}
        </p>
        <p className="muted">{texts.verify.help}</p>
        <label>
          {texts.verify.code}
          <input
            className="verify__code"
            inputMode="numeric"
            autoComplete="one-time-code"
            pattern="[0-9]{6}"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            required
          />
        </label>
        <StatusMessage error={error} />
        {notice && !error && <p className="banner">{notice}</p>}
        <button className="button" disabled={code.length !== 6 || !phone}>
          {texts.verify.submit}
        </button>
        <button
          type="button"
          className="button button--secondary"
          disabled={wait > 0 || !phone}
          onClick={() => void resend()}
        >
          {wait > 0 ? texts.verify.resendIn(wait) : texts.verify.resend}
        </button>
      </form>
      <Link to="/ingresar">{texts.auth.goToLogin}</Link>
    </main>
  );
}
