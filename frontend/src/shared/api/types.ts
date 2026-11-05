// Tipos de las respuestas de la API (los campos vienen en inglés, igual que el backend)
export interface LivePrice {
  quoted_at: string; // hora de la cotización en la bolsa (ya en hora de Lima)
  date: string;
  cents_per_pound: number;
  price_soles: number;
  previous_close_soles: number | null;
  change_soles: number | null;
  change_pct: number | null;
  unit: string;
  market: string;
  market_open: boolean;
  stale: boolean;
  sources: string[];
  local_estimates: LocalEstimate[];
  exchange_rate?: number | null; // S/ por US$ usado en la conversión (nota «¿Cómo se calcula?»)
  exchange_source?: string | null; // dólar en vivo (web) o BCRP
  exchange_rated_at?: string | null; // hora del dólar en vivo (null si es el oficial del día)
}

export type CoffeeType = "convencional" | "organico" | "especial";

/** Precio estimado en Jaén: la bolsa × el porcentaje que pagan las cooperativas (HU12). */
export interface LocalEstimate {
  coffee_type: CoffeeType;
  estimated_soles: number;
  ratio_pct: number;
  observations: number;
  first_day: string;
  last_day: string;
  few_data: boolean;
  synthetic_observations?: number; // precios sintéticos de demostración entre los usados
}

export interface LocalPriceObservation {
  id: number;
  observed_at: string;
  cooperative: string;
  coffee_type: CoffeeType;
  paid_soles: number;
  exchange_soles: number;
  ratio_pct: number;
}

export interface HistoryPoint {
  date: string;
  time?: string; // solo en el gráfico de hoy (minuto a minuto)
  price_soles: number;
}

export type HistoryPeriod = "today" | "30" | "90";

export interface PriceHistory {
  period: HistoryPeriod;
  points: HistoryPoint[];
}

export interface ForecastPoint {
  date: string;
  expected_soles: number;
  lower_soles: number;
  upper_soles: number;
}

export interface Forecast {
  generated_on: string;
  model: string;
  mape: number;
  disclaimer: string;
  points: ForecastPoint[];
}

export type Verdict = "Vender ahora" | "Esperar" | "Sin señal clara" | "Sin datos suficientes";

export interface SellingAdvice {
  verdict: Verdict;
  reason: string;
  current_soles: number | null;
  target_date: string | null;
  target_soles: number | null;
  change_pct: number | null;
  hit_rate_pct: number | null;
  disclaimer: string;
  sources: string[];
}

export interface AdvisorAnswer {
  answer: string;
  sources: string[];
  used_tool: string | null;
}

export interface Session {
  access_token: string;
}

/** Cooperativa del catálogo que mantiene el equipo. */
export interface Cooperative {
  id: number;
  name: string;
  location: string;
  website: string | null;
  active: boolean;
}

/** Respuesta del registro: la cuenta espera el código enviado al correo. */
export interface CodeDelivery {
  phone: string;
  email: string | null; // enmascarado: «lu***@gmail.com»
  delivered_by: "whatsapp" | "email" | null; // null: el código solo lo tiene el equipo
  team_whatsapp: string | null; // para pedir el código al equipo si no llegó
}

export interface PendingVerification extends CodeDelivery {
  verification_required: true;
}

/** GET /api/auth/me: quién inició sesión en esta pestaña. */
export interface Profile {
  name: string | null;
  display_name: string; // el nombre o, si no lo dio, el celular
  phone: string;
  email: string | null;
  role: "farmer" | "admin";
}
