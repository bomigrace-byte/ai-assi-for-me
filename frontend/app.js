import { getAdminKey, setAdminKey } from "./admin-key.js";
import { clearSessionToken, getSessionToken } from "./session-token.js";

const API_BASE = window.APP_CONFIG?.API_BASE || "http://127.0.0.1:8000";
const state = document.querySelector("#dashboard-state");
const rankingSection = document.querySelector("#ranking-section");
const rankingList = document.querySelector("#ranking-list");
const periodSelect = document.querySelector("#period-select");
const detailSection = document.querySelector("#detail-section");
const detailTitle = document.querySelector("#detail-title");
const detailSummary = document.querySelector("#detail-summary");
const weeklyChart = document.querySelector("#weekly-chart");
const snapshotValue = document.querySelector("#snapshot-value");
const snapshotDate = document.querySelector("#snapshot-date");
let rankingResults = [];
const THEME_KEY = "ai-tech-trend-radar.theme";
let activeConversationId = null;

function showState(message, isError = false) {
  state.hidden = false;
  state.innerHTML = `<p>${message}</p>`;
  state.classList.toggle("error-state", isError);
  rankingSection.hidden = true;
}

function formatNumber(value) {
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 1 }).format(value ?? 0);
}

function renderRanking(results) {
  rankingResults = results;
  state.hidden = true;
  rankingSection.hidden = false;
  rankingList.innerHTML = results.map((item, index) => {
    const momentum = item.momentum_change_percent == null ? "기준 부족" : `${item.momentum_change_percent > 0 ? "+" : ""}${item.momentum_change_percent.toFixed(1)}%`;
    const statusClass = item.status === "slowing" ? "slowing" : "";
    return `<article class="ranking-card" tabindex="0" data-technology="${item.technology}">
      <div class="rank-number">0${index + 1}</div>
      <div><h3 class="tech-name">${item.technology}</h3><p class="repo-name">${item.repository}</p><p class="evidence">${item.reason}</p></div>
      <div class="metric"><strong>${formatNumber(item.weekly_new_stars_average)}</strong><small>주당 평균 신규 Star</small><br /><span class="momentum ${statusClass}">Momentum ${momentum}</span></div>
    </article>`;
  }).join("");
  rankingList.querySelectorAll("[data-technology]").forEach((card) => {
    card.addEventListener("click", () => loadDetail(card.dataset.technology));
    card.addEventListener("keydown", (event) => { if (event.key === "Enter") loadDetail(card.dataset.technology); });
  });
  [document.querySelector("#compare-a"), document.querySelector("#compare-b")].forEach((select) => {
    select.innerHTML = rankingResults.map((item) => `<option value="${item.technology}">${item.technology}</option>`).join("");
  });
  if (rankingResults[1]) document.querySelector("#compare-b").value = rankingResults[1].technology;
}

async function compareTechnologies() {
  const first = document.querySelector("#compare-a").value;
  const second = document.querySelector("#compare-b").value;
  const resultElement = document.querySelector("#compare-result");
  if (!first || !second || first === second) return;
  try {
    const response = await fetch(`${API_BASE}/api/data/compare?technologies=${encodeURIComponent(first)},${encodeURIComponent(second)}&period=${periodSelect.value}`);
    if (!response.ok) throw new Error(`API ${response.status}`);
    const payload = await response.json();
    resultElement.hidden = false;
    resultElement.innerHTML = payload.results.map((item) => `<div class="summary-tile"><span>${item.technology}</span><strong>${formatNumber(item.weekly_new_stars_average)} Star/주</strong><small>Momentum ${item.momentum_change_percent == null ? "기준 부족" : item.momentum_change_percent.toFixed(1) + "%"}</small></div>`).join("");
  } catch (error) {
    resultElement.hidden = false;
    resultElement.innerHTML = '<div class="summary-tile"><span>비교 실패</span><strong>데이터를 확인해 주세요.</strong></div>';
    console.error(error);
  }
}

function renderDemoRows(rows) {
  document.querySelector("#demo-list").innerHTML = rows.map((row) => `<div class="demo-row"><span>${row.technology} · ${row.date} · ${row.value} Star</span><button type="button" data-demo-id="${row.id}">삭제</button></div>`).join("");
  document.querySelectorAll("[data-demo-id]").forEach((button) => button.addEventListener("click", () => deleteDemo(button.dataset.demoId)));
}

async function loadDemoRows() {
  const response = await fetch(`${API_BASE}/api/data?metric=weekly_new_stars&source=manual_demo`);
  if (response.ok) renderDemoRows((await response.json()).filter((row) => row.source === "manual_demo"));
}

async function deleteDemo(id) {
  const response = await fetch(`${API_BASE}/api/data/${id}`, { method: "DELETE", headers: { "X-Admin-Key": getAdminKey() || "" } });
  document.querySelector("#demo-status").textContent = response.ok ? "Demo 데이터를 삭제했습니다." : "삭제 권한을 확인해 주세요.";
  await loadDemoRows();
}

document.querySelector("#demo-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const keyInput = document.querySelector("#admin-key-input");
  setAdminKey(keyInput.value);
  const body = {
    technology: document.querySelector("#demo-technology").value,
    repository: document.querySelector("#demo-repository").value,
    date: document.querySelector("#demo-date").value,
    week_start_epoch: Math.floor(new Date(document.querySelector("#demo-date").value).getTime() / 1000),
    value: Number(document.querySelector("#demo-value").value),
  };
  const response = await fetch(`${API_BASE}/api/data`, { method: "POST", headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() || "" }, body: JSON.stringify(body) });
  document.querySelector("#demo-status").textContent = response.ok ? "Demo 데이터를 저장했습니다. 분석에는 포함되지 않습니다." : "저장 권한 또는 입력값을 확인해 주세요.";
  if (response.ok) await loadDemoRows();
});

loadDemoRows().catch(() => {});

function sessionHeaders() { return { "X-Session-Token": getSessionToken() }; }

async function loadConversations() {
  const response = await fetch(`${API_BASE}/api/conversations`, { headers: sessionHeaders() });
  if (!response.ok) return;
  const conversations = await response.json();
  const list = document.querySelector("#conversation-list-items");
  list.innerHTML = conversations.length ? conversations.map((item) => `<button class="conversation-item ${item.id === activeConversationId ? "active" : ""}" data-conversation-id="${item.id}">${item.title}</button>`).join("") : '<span class="muted">아직 대화가 없습니다.</span>';
  list.querySelectorAll("[data-conversation-id]").forEach((button) => button.addEventListener("click", () => loadConversation(button.dataset.conversationId)));
}

async function loadConversation(id) {
  const response = await fetch(`${API_BASE}/api/conversations/${id}`, { headers: sessionHeaders() });
  if (!response.ok) return;
  activeConversationId = id;
  const conversation = await response.json();
  document.querySelector("#chat-messages").innerHTML = conversation.messages.length ? conversation.messages.map((message) => `<div class="chat-message ${message.role}">${message.content}</div>`).join("") : '<div class="chat-empty">첫 질문을 입력해 보세요.</div>';
  await loadConversations();
}

document.querySelector("#new-session").addEventListener("click", () => {
  clearSessionToken();
  activeConversationId = null;
  document.querySelector("#chat-messages").innerHTML = '<div class="chat-empty">새 익명 세션이 시작됐습니다.</div>';
  loadConversations().catch(() => {});
});

document.querySelector("#chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.querySelector("#chat-input");
  const message = input.value.trim();
  if (!message) return;
  const response = await fetch(`${API_BASE}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json", ...sessionHeaders() }, body: JSON.stringify({ message, conversation_id: activeConversationId }) });
  if (!response.ok) { document.querySelector("#chat-messages").insertAdjacentHTML("beforeend", '<div class="chat-message assistant">현재 Chat Backend를 사용할 수 없습니다.</div>'); return; }
  const result = await response.json();
  activeConversationId = result.conversation_id;
  input.value = "";
  await loadConversation(activeConversationId);
});

loadConversations().catch(() => {});

async function loadDetail(technology) {
  detailSection.hidden = false;
  detailTitle.textContent = technology;
  detailSummary.innerHTML = '<div class="state-card"><p>상세 신호를 불러오는 중입니다.</p></div>';
  try {
    const [summaryResponse, historyResponse, snapshotResponse] = await Promise.all([
      fetch(`${API_BASE}/api/data/summary?technology=${encodeURIComponent(technology)}&period=${periodSelect.value}`),
      fetch(`${API_BASE}/api/data?technology=${encodeURIComponent(technology)}&metric=weekly_new_stars`),
      fetch(`${API_BASE}/api/data/snapshots?technology=${encodeURIComponent(technology)}`),
    ]);
    if (!summaryResponse.ok || !historyResponse.ok || !snapshotResponse.ok) throw new Error("detail API error");
    const summary = await summaryResponse.json();
    const history = (await historyResponse.json()).slice(-52);
    const snapshots = await snapshotResponse.json();
    detailSummary.innerHTML = [
      ["최근 평균", `${formatNumber(summary.weekly_new_stars_average)} Star`],
      ["Momentum", summary.momentum_change_percent == null ? "기준 부족" : `${summary.momentum_change_percent.toFixed(1)}%`],
      ["상태", summary.status],
      ["관측 주", `${summary.observed_recent}주`],
    ].map(([label, value]) => `<div class="summary-tile"><span>${label}</span><strong>${value}</strong></div>`).join("");
    const max = Math.max(...history.map((row) => row.value), 1);
    weeklyChart.innerHTML = history.map((row) => `<span class="bar" title="${row.date}: ${row.value}" style="height:${Math.max(3, (row.value / max) * 100)}%"></span>`).join("");
    const snapshot = snapshots[0];
    snapshotValue.textContent = snapshot ? formatNumber(snapshot.current_stargazer_count) : "—";
    snapshotDate.textContent = snapshot ? `수집 ${new Date(snapshot.collected_at).toLocaleDateString("ko-KR")}` : "동기화 전";
    detailSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    detailSummary.innerHTML = '<div class="state-card"><p>상세 데이터를 불러오지 못했습니다.</p></div>';
    console.error(error);
  }
}

async function loadRanking() {
  showState("분석 신호를 불러오는 중입니다.");
  try {
    const response = await fetch(`${API_BASE}/api/data/ranking?period=${periodSelect.value}&limit=5`);
    if (!response.ok) throw new Error(`API ${response.status}`);
    const payload = await response.json();
    if (!payload.results?.length) {
      showState("아직 표시할 분석 데이터가 없습니다. GitHub 동기화 후 다시 시도해 주세요.");
      return;
    }
    renderRanking(payload.results);
  } catch (error) {
    showState("분석 데이터를 불러오지 못했습니다. Backend가 실행 중인지 확인해 주세요.", true);
    console.error(error);
  }
}

document.querySelector("#refresh-button").addEventListener("click", loadRanking);
periodSelect.addEventListener("change", loadRanking);
document.querySelector("#theme-toggle").addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem(THEME_KEY, document.body.classList.contains("dark") ? "dark" : "light");
});
if (localStorage.getItem(THEME_KEY) === "dark") document.body.classList.add("dark");
document.querySelector("#detail-close").addEventListener("click", () => { detailSection.hidden = true; });
document.querySelector("#compare-button").addEventListener("click", compareTechnologies);
function downloadExport(format) {
  const link = document.createElement("a");
  link.href = `${API_BASE}/api/export/${format}?metric=weekly_new_stars`;
  link.target = "_blank";
  link.rel = "noopener";
  link.click();
}
document.querySelector("#export-json").addEventListener("click", () => downloadExport("json"));
document.querySelector("#export-csv").addEventListener("click", () => downloadExport("csv"));
loadRanking();
