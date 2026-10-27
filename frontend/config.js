// 로컬 미리보기는 tools/serve_frontend.py의 같은 출처 API 프록시를 사용합니다.
// 배포 환경은 Render Backend를 직접 호출합니다.
window.APP_CONFIG = {
  API_BASE: ["127.0.0.1", "localhost"].includes(window.location.hostname)
    ? window.location.origin
    : "https://ai-assi-for-me.onrender.com",
};
