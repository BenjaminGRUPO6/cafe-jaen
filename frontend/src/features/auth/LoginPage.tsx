import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../../shared/api/client";
import { useAuth } from "../../shared/auth/AuthContext";
import { Brand } from "../../shared/components/Brand";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<ApiError | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await login(phone, password);
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
      <h1>{texts.auth.loginTitle}</h1>
      <form className="form card" onSubmit={onSubmit}>
        <label>
          {texts.auth.phone}
          <input
            inputMode="numeric"
            autoComplete="tel"
            maxLength={9}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />
        </label>
        <label>
          {texts.auth.password}
          <input
            type="password"
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
