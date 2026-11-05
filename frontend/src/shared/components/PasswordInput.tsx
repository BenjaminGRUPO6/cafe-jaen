import { useState, type InputHTMLAttributes } from "react";
import { EyeIcon, EyeOffIcon } from "../motion/icons";
import { texts } from "../texts/es";

/** Campo de contraseña con el botón del ojo para verla u ocultarla. */
export function PasswordInput(props: Omit<InputHTMLAttributes<HTMLInputElement>, "type">) {
  const [visible, setVisible] = useState(false);
  return (
    <span className="password-field">
      <input {...props} type={visible ? "text" : "password"} />
      <button
        type="button"
        className="password-field__toggle"
        aria-label={visible ? texts.auth.hidePassword : texts.auth.showPassword}
        aria-pressed={visible}
        onClick={() => setVisible((value) => !value)}
      >
        {visible ? <EyeOffIcon /> : <EyeIcon />}
      </button>
    </span>
  );
}
