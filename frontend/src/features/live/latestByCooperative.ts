import type { CoffeeType, LocalPriceObservation } from "../../shared/api/types";

/** Último precio que pagó cada cooperativa por un tipo de café (el más reciente primero). */
export function latestByCooperative(
  observations: LocalPriceObservation[],
  coffeeType: CoffeeType,
): LocalPriceObservation[] {
  const latest = new Map<string, LocalPriceObservation>();
  for (const item of observations) {
    if (item.coffee_type !== coffeeType) continue;
    const current = latest.get(item.cooperative);
    if (!current || item.observed_at > current.observed_at) latest.set(item.cooperative, item);
  }
  return [...latest.values()].sort((a, b) => b.observed_at.localeCompare(a.observed_at));
}
