import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../../shared/api/client";
import { useAuth } from "../../shared/auth/AuthContext";
import { Brand } from "../../shared/components/Brand";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { PasswordInput } from "../../shared/components/PasswordInput";
import { texts } from "../../shared/texts/es";
import { verifyPath } from "./VerifyPage";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<ApiError | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await login(identifier, password);
      navigate("/");
    } catch (caught) {
      const failure = caught as ApiError;
      // 403: la contraseña es correcta pero la cuenta aún no confirmó el código del correo
      if (failure.status === 403) {
        navigate(verifyPath(String(failure.body.phone ?? identifier)));
        return;
      }
      setError(failure);
    }
  };

  return (
    <main className="content auth">
      <div className="auth__hero tile tile--grano">
        <Brand />
        <p className="auth__tagline">{texts.auth.tagline}</p>
      </div>
      <h1>{texts.auth.loginTitle}</h1>
      <form className="form card" onSubmit={onSubmit}>
        <label>
          {texts.auth.identifier}
          <input
            autoComplete="username"
            autoCapitalize="none"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
          />
        </label>
        <label>
          {texts.auth.password}
          <PasswordInput
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <StatusMessage error={error} />
        <button className="button">{texts.auth.login}</button>
      </form>
      <Link to="/registro">{texts.auth.goToRegister}</Link>
    </main>
  );
}
