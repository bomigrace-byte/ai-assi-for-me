# 최종 데모 시나리오

## 로컬 실행

1. Backend를 `uvicorn backend.main:app --reload --port 8000`으로 실행한다.
2. Frontend를 `python -m http.server 3000 --directory frontend`로 실행한다.
3. `http://127.0.0.1:3000`에서 최근 13주 랭킹과 빈 데이터 상태를 확인한다.

## 핵심 흐름

1. 기간을 4주·13주·26주·52주로 바꾸고 랭킹 기준이 함께 변경되는지 확인한다.
2. 기술 상세를 열어 최근 52주 `weekly_new_stars` 차트와 별도 Current Snapshot을 확인한다.
3. 두 기술을 선택해 Compare 결과와 주당 평균 신규 Star·Momentum 근거를 확인한다.
4. Chat에서 성장세 질문을 보내고 Conversation 저장·목록·재조회가 되는지 확인한다.
5. JSON/CSV 버튼으로 현재 필터 범위를 Export한다.
6. 관리자 키를 입력해 Demo 행을 저장한 뒤, 해당 행이 분석에 섞이지 않는지 확인한다.
7. 새로고침 후 관리자 키가 복원되지 않고, 일반 세션 토큰만 `localStorage`에서 유지되는지 확인한다.
8. MCP stdio Client로 `tools/list`와 `tools/call`을 호출한다.

## 검증 증적

- Codex 브라우저에서 Dashboard·Compare·Admin/Demo·Chat·Dark Mode UI 로드 확인
- 터미널에서 전체 Acceptance, API 보호, 세션 격리, Export, MCP 호출 확인
- 외부 배포는 Render/Vercel 자격증명과 실제 URL이 제공된 뒤 동일 시나리오를 재실행한다.
