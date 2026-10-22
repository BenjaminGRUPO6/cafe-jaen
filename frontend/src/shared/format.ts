// Formato peruano: coma decimal y sin separador de miles (igual que el asesor)
export function formatSoles(value: number): string {
  return `S/ ${value.toFixed(2).replace(".", ",")}`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1).replace(".", ",")} %`;
}

export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

export function formatDateTime(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(date.getDate())}/${pad(date.getMonth() + 1)} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// La API ya entrega la hora en Lima («2026-11-04T08:55:00-05:00»): se toma tal cual
export function formatTime(isoDateTime: string): string {
  return isoDateTime.slice(11, 16);
}

export function formatCents(value: number): string {
  return `${value.toFixed(2).replace(".", ",")} ¢/lb`;
}
