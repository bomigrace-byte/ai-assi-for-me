const SESSION_TOKEN_KEY = "ai-tech-trend-radar.session-token";

function createToken() {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function getSessionToken() {
  let token = localStorage.getItem(SESSION_TOKEN_KEY);
  if (!token || !/^[0-9a-f]{64}$/.test(token)) {
    token = createToken();
    localStorage.setItem(SESSION_TOKEN_KEY, token);
  }
  return token;
}

export function clearSessionToken() {
  localStorage.removeItem(SESSION_TOKEN_KEY);
}
