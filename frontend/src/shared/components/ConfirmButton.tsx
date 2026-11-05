import { useEffect, useState, type ReactNode } from "react";
import { texts } from "../texts/es";

/**
 * Botón de dos toques para acciones que no se pueden deshacer (borrar): el primero pide
 * confirmación y el segundo ejecuta. Sin ventanas emergentes del navegador.
 */
export function ConfirmButton({
  onConfirm,
  children,
  disabled = false,
  label,
}: {
  onConfirm: () => void;
  children: ReactNode;
  disabled?: boolean;
  label: string;
}) {
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    if (!asking) return;
    const timer = window.setTimeout(() => setAsking(false), 4000); // se cancela solo
    return () => window.clearTimeout(timer);
  }, [asking]);

  return (
    <button
      type="button"
      className={`icon-button ${asking ? "icon-button--danger" : ""}`}
      aria-label={asking ? texts.common.confirmDelete : label}
      disabled={disabled}
      onClick={() => {
        if (asking) {
          setAsking(false);
          onConfirm();
        } else {
          setAsking(true);
        }
      }}
    >
      {asking ? texts.common.confirmDelete : children}
    </button>
  );
}
