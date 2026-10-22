import { readStored } from "../storage";
import { texts } from "../texts/es";

export const TOKEN_KEY = "cafe-jaen.token";
const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

/** Error con un mensaje listo para mostrar al caficultor. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = readStored(TOKEN_KEY);
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(texts.common.genericError, 0);
  }
  if (!response.ok) {
    // FastAPI devuelve el mensaje en "detail"; si es una lista (validación), se usa el genérico
    const body = await response.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : texts.common.genericError;
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};
