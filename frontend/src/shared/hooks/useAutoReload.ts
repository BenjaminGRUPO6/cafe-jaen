import { useEffect, useRef } from "react";

/** Vuelve a pedir los datos cada `ms` milisegundos mientras la pantalla está abierta. */
export function useAutoReload(reload: () => void, ms: number): void {
  // `reload` cambia en cada render: se guarda en una referencia para no reiniciar el temporizador
  const latest = useRef(reload);
  useEffect(() => {
    latest.current = reload;
  }, [reload]);
  useEffect(() => {
    const timer = window.setInterval(() => latest.current(), ms);
    return () => window.clearInterval(timer);
  }, [ms]);
}
