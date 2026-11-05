// Mismas constantes que el backend (market/domain/quintal_price.py)
const KG_PER_QUINTAL = 46;
const POUNDS_PER_KG = 2.20462262;
export const POUNDS_PER_QUINTAL = KG_PER_QUINTAL * POUNDS_PER_KG; // 101,41 libras

/** Pasos de la conversión ¢/lb → S/ por quintal, para la nota «¿Cómo se calcula?». */
export function priceSteps(centsPerPound: number) {
  const usdPerPound = centsPerPound / 100;
  return { usdPerPound, usdPerQuintal: usdPerPound * POUNDS_PER_QUINTAL };
}
