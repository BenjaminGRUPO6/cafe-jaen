import { readStored } from "../storage";
import { TOKEN_KEY } from "./client";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";
const RETRY_MS = 5000;

export interface SseEvent {
  event: string;
  data: string;
}

/** Separa los eventos completos de un texto Server-Sent Events; devuelve lo que sobra. */
export function parseSse(buffer: string): { events: SseEvent[]; rest: string } {
  const blocks = buffer.split("\n\n");
  const rest = blocks.pop() ?? "";
  const events: SseEvent[] = [];
  for (const block of blocks) {
    let event = "message";
    const data: string[] = [];
    for (const line of block.split("\n")) {
      if (line.startsWith(":")) continue; // comentario (latido para mantener la conexión)
      if (line.startsWith("event:")) event = line.slice(6).trim();
      if (line.startsWith("data:")) data.push(line.slice(5).trim());
    }
    if (data.length) events.push({ event, data: data.join("\n") });
  }
  return { events, rest };
}

/**
 * Escucha un flujo SSE de la API con el token de sesión (EventSource no permite cabeceras,
 * por eso se usa fetch). Si se corta, se reconecta solo cada 5 s hasta que se cancele.
 */
export function listen(
  path: string,
  onEvent: (event: SseEvent) => void,
  onError: () => void,
): () => void {
  const controller = new AbortController();

  const connect = async () => {
    while (!controller.signal.aborted) {
      try {
        const token = readStored(TOKEN_KEY);
        const response = await fetch(`${BASE_URL}${path}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          signal: controller.signal,
        });
        if (!response.ok || !response.body) throw new Error(String(response.status));
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        for (;;) {
          const { value, done } = await reader.read();
          if (done) break;
          const parsed = parseSse(buffer + decoder.decode(value, { stream: true }));
          buffer = parsed.rest;
          parsed.events.forEach(onEvent);
        }
      } catch {
        if (controller.signal.aborted) return;
        onError();
      }
      await new Promise((resolve) => setTimeout(resolve, RETRY_MS));
    }
  };

  void connect();
  return () => controller.abort();
}
