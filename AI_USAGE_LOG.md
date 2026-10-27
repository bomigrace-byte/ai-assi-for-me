# AI Usage Log

## 2026-10-06 — 구현 지원 기록

- 사용 목적: PRD·TASK 기준의 데이터 모델, 분석 규칙, API, UI, Chat, MCP 구현과 검증
- AI가 작성·수정한 범위: Backend FastAPI 모듈, Frontend Vanilla HTML/CSS/JavaScript, 검증 테스트, Architecture·README·결정 기록
- 사람이 확인해야 하는 범위: GitHub API 운영 토큰, Firebase 자격증명, OpenAI 키, Render/Vercel 계정과 실제 배포 URL
- 데이터 원칙: GitHub 수집 행만 분석에 사용하고, 수동 Demo 행은 `analysis_eligible=false`로 유지
- AI 계산 제한: LLM은 숫자를 계산하지 않으며 Backend Tool 결과만 답변 근거로 사용
- 검증 방식: unittest, Python compile, Node syntax, FastAPI OpenAPI/HTTP smoke test, MCP stdio 호출, Codex 브라우저 UI 확인

## 2026-10-28 — 읽기 비용 절약·디자인·배포 및 문서 정합성

- AI 지원 범위: 분석 결과 사전 계산, 기술·세션 조건 조회, 관련 테스트, Aurora Radar/Signal Studio 색감의 테마 변경, README·Architecture·결정/시연/배포 문서 정리
- 사람이 보유·관리하는 값: Firebase·GitHub·OpenAI·Render 관리자 비밀값. AI는 문서나 프론트엔드에 비밀값을 복사하지 않음
- 검증: 로컬 자동 테스트 19개, 프론트엔드 JS 문법 검사, GitHub `main` 커밋 `6cbb676`, Render Live·Vercel success, 공개 Frontend 새 테마 파일, Backend `/health` 200
- 미완료 검증: Firestore 할당량 초과로 공개 랭킹 503. 원격 분석 문서 생성·사용량 감소, Chat·Demo CRUD·모바일 전체 흐름은 복구 후 사람과 함께 재확인 필요
