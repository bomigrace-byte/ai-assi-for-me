let adminKey = null;

export function setAdminKey(value) {
  adminKey = value.trim() || null;
}

export function getAdminKey() {
  return adminKey;
}

export function clearAdminKey() {
  adminKey = null;
}
