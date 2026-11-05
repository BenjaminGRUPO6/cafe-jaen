import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../../shared/api/client";
import type { CodeDelivery } from "../../shared/api/types";
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
  const pending = useLocation().state as CodeDelivery | null;
  const phone = pending?.phone ?? params.get("telefono") ?? "";
  const [delivery, setDelivery] = useState<CodeDelivery | null>(pending);
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
      setDelivery(await api.post<CodeDelivery>("/auth/resend", { phone }));
      setNotice(texts.verify.resent);
      setWait(RESEND_SECONDS);
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
      <h1>{texts.verify.title}</h1>
      <form className="form card" onSubmit={onSubmit}>
        <p>{deliveryText(delivery, phone)}</p>
        <p className="muted">{texts.verify.help}</p>
        {delivery?.team_whatsapp && (
          <a
            className="button button--secondary"
            href={askTeamLink(delivery.team_whatsapp, phone)}
            target="_blank"
            rel="noopener noreferrer"
          >
            {texts.verify.askTeam}
          </a>
        )}
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

/** A dónde salió el código (WhatsApp, correo) o, si no salió, que lo pida al equipo. */
function deliveryText(delivery: CodeDelivery | null, phone: string): string {
  if (delivery === null) return texts.verify.sentSomewhere;
  if (delivery.delivered_by === "whatsapp") return texts.verify.sentWhatsApp(phone);
  if (delivery.delivered_by === "email" && delivery.email) {
    return texts.verify.sentEmail(delivery.email);
  }
  return texts.verify.notSent;
}

/** Abre WhatsApp con un mensaje listo para pedir el código al equipo. */
export function askTeamLink(teamPhone: string, phone: string): string {
  return `https://wa.me/51${teamPhone}?text=${encodeURIComponent(texts.verify.askTeamText(phone))}`;
}
