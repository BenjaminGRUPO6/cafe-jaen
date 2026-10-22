import type { LivePrice } from "../../shared/api/types";
import { readStored, writeStored } from "../../shared/storage";

const KEY = "cafe-jaen.last-price";

export interface CachedPrice {
  price: LivePrice;
  savedAt: string; // ISO
}

/** Guarda el último precio recibido para mostrarlo sin conexión (HU09). */
export function saveLastPrice(price: LivePrice, now: Date = new Date()): void {
  writeStored(KEY, JSON.stringify({ price, savedAt: now.toISOString() }));
}

export function loadLastPrice(): CachedPrice | null {
  const raw = readStored(KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as CachedPrice;
  } catch {
    return null;
  }
}
