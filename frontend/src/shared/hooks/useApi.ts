import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";

interface ApiState<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
  reload: () => void;
}

interface Result<T> {
  key: string;
  data: T | null;
  error: ApiError | null;
}

/** Hace un GET a la API al montar el componente y cada vez que cambia `path`. */
export function useApi<T>(path: string): ApiState<T> {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<Result<T> | null>(null);
  const key = `${path}#${attempt}`; // identifica la consulta en curso

  useEffect(() => {
    let active = true; // evita actualizar el estado si el usuario ya cambió de pantalla
    api
      .get<T>(path)
      .then((data) => active && setResult({ key, data, error: null }))
      .catch((caught: unknown) => {
        const error = caught instanceof ApiError ? caught : new ApiError(String(caught), 0);
        if (active) setResult({ key, data: null, error });
      });
    return () => {
      active = false;
    };
  }, [path, key]);

  const isCurrent = result?.key === key;
  // Al «volver a calcular» se mantiene el dato anterior de la misma ruta mientras llega el nuevo
  const samePath = result?.key.startsWith(`${path}#`) ?? false;
  return {
    data: isCurrent || samePath ? (result?.data ?? null) : null,
    error: isCurrent ? result.error : null,
    loading: !isCurrent,
    reload: () => setAttempt((n) => n + 1),
  };
}
