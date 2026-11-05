// localStorage puede fallar (modo privado, almacenamiento lleno): nunca debe romper la app
export function readStored(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeStored(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // Sin almacenamiento la app sigue funcionando, solo sin recordar datos
  }
}

/**
 * Sesión por pestaña: cada pestaña guarda su propia sesión (sessionStorage), así dos cuentas
 * abiertas en el mismo navegador no se pisan. Además se recuerda la última sesión
 * (localStorage) para que una pestaña nueva, o la app al día siguiente, entre sin pedir la
 * contraseña (la sesión dura 30 días).
 */
export function readSession(key: string): string | null {
  try {
    const own = sessionStorage.getItem(key);
    if (own !== null) return own;
    const remembered = localStorage.getItem(key);
    if (remembered !== null) sessionStorage.setItem(key, remembered);
    return remembered;
  } catch {
    return readStored(key);
  }
}

export function writeSession(key: string, value: string | null): void {
  let own: string | null = null;
  try {
    own = sessionStorage.getItem(key);
    if (value === null) sessionStorage.removeItem(key);
    else sessionStorage.setItem(key, value);
  } catch {
    // Sin sessionStorage se usa solo la sesión recordada
  }
  if (value !== null) {
    writeStored(key, value);
    return;
  }
  // Al salir solo se olvida la sesión recordada si era la de esta pestaña
  if (own === null || readStored(key) === own) writeStored(key, null);
}
