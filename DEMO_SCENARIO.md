# 최종 데모 시나리오

> 2026-10-28 상태: 배포는 완료됐지만 Firestore 할당량 초과로 데이터 기능의 최신 실서비스 시연은 보류한다. 할당량 복구 후 아래 순서를 실행하고 결과를 `DEPLOYMENT_CHECKLIST.md`에 반영한다.

## 접속 준비

1. 공개 [Frontend](https://ai-assi-for-me-frontend.vercel.app/)와 [Backend API 문서](https://ai-assi-for-me.onrender.com/docs)를 연다.
2. `/health` 200과 별개로 `/api/data/ranking?period=13w&limit=5`의 정상 응답을 확인한다. `503 DATASTORE_QUOTA_EXCEEDED`라면 시연을 중단하고 반복 호출하지 않는다.
3. 로컬 미리보기가 필요하면 `.\.venv\Scripts\python.exe tools\serve_frontend.py`로 `http://127.0.0.1:3000`을 연다. 이 서버는 기본적으로 배포 Backend를 프록시하므로 원격 데이터·Chat에 영향을 준다. 로컬 Backend를 쓰려면 서버 시작 전 PowerShell에서 `$env:PREVIEW_BACKEND_URL = "http://127.0.0.1:8000"`을 설정하고 Backend도 실행한다. 단순 `python -m http.server`는 현재 같은 출처 API 프록시를 제공하지 않는다.

## 핵심 흐름

1. 상위 5개 랭킹을 보고 기간을 4주·13주·26주·52주로 바꿔 표시가 갱신되는지 확인한다.
2. 기술 카드를 열어 최근 52주 `weekly_new_stars` 차트와 별도 현재 누적 Star를 확인한다.
3. 두 기술을 선택해 Compare 결과와 주당 평균 신규 Star·Momentum을 Summary와 대조한다.
4. AI Chat에서 성장세 질문을 보내고 답변 근거·Conversation 저장·목록·불러오기를 확인한다. “새 대화” 후 이전 대화가 남는지, 실패한 Chat이 빈 대화를 남기지 않는지도 확인한다.
5. 다크/라이트 테마를 전환하고 새로고침 후 선택이 유지되는지 확인한다. 작은 화면에서 랭킹·비교·Chat·데이터 관리가 사용 가능한지 확인한다.
6. 관리자 키를 입력해 Demo 행을 저장·조회·삭제하고, 이 행이 공식 분석에 섞이지 않는지 확인한다. 관리자 키가 새로고침 후 복원되지 않는지 확인한다.
7. JSON/CSV Export와 MCP stdio `tools/list`·`tools/call`은 별도 검증한다. Export와 동기화는 Firestore 사용량이 크므로 할당량 상태를 먼저 확인한다.

## 현재 증적과 미완료

- 커밋 `6cbb676`의 Render Live·Vercel success, Backend `/health` 200, 운영 Frontend의 새 테마 파일 제공을 확인했다.
- 로컬 자동 테스트 19개와 JavaScript 문법 검사는 통과했다.
- 같은 배포의 랭킹 API는 Firebase 할당량 초과로 503이었다. 새 분석 문서 생성·Chat·Demo CRUD·모바일 시연은 **아직 재검증하지 않았다**.
