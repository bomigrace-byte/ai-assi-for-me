const THEME_KEY = "ai-tech-trend-radar.theme";
const themeToggle = document.querySelector("#theme-toggle");

function savedTheme() {
  try {
    return localStorage.getItem(THEME_KEY);
  } catch {
    return null;
  }
}

function setTheme(theme) {
  const isLight = theme === "light";
  document.body.classList.toggle("light", isLight);
  document.body.classList.remove("dark");
  themeToggle.textContent = isLight ? "☾" : "☼";
  themeToggle.setAttribute("aria-label", isLight ? "다크 모드로 전환" : "라이트 모드로 전환");
  themeToggle.setAttribute("aria-pressed", String(isLight));
}

setTheme(savedTheme());
themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.classList.contains("light") ? "dark" : "light";
  setTheme(nextTheme);
  try {
    localStorage.setItem(THEME_KEY, nextTheme);
  } catch {
    // Storage may be blocked in private or embedded browsers; the switch still works.
  }
});
