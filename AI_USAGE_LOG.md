# AI Usage Log

## 2026-10-06 — 구현 지원 기록

- 사용 목적: PRD·TASK 기준의 데이터 모델, 분석 규칙, API, UI, Chat, MCP 구현과 검증
- AI가 작성·수정한 범위: Backend FastAPI 모듈, Frontend Vanilla HTML/CSS/JavaScript, 검증 테스트, Architecture·README·결정 기록
- 사람이 확인해야 하는 범위: GitHub API 운영 토큰, Firebase 자격증명, OpenAI 키, Render/Vercel 계정과 실제 배포 URL
- 데이터 원칙: GitHub 수집 행만 분석에 사용하고, 수동 Demo 행은 `analysis_eligible=false`로 유지
- AI 계산 제한: LLM은 숫자를 계산하지 않으며 Backend Tool 결과만 답변 근거로 사용
- 검증 방식: unittest, Python compile, Node syntax, FastAPI OpenAPI/HTTP smoke test, MCP stdio 호출, Codex 브라우저 UI 확인
