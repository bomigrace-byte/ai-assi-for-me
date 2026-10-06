/**
 * Admin key is intentionally process-memory-only.
 * Do not replace this with localStorage, sessionStorage, cookies, or a build-time env value.
 */
let adminKey: string | null = null;

export function setAdminKey(value: string): void {
  adminKey = value.trim() || null;
}

export function getAdminKey(): string | null {
  return adminKey;
}

export function clearAdminKey(): void {
  adminKey = null;
}
