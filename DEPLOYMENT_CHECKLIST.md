# 배포 및 제출 확인

> 기준: 2026-10-28, GitHub `main` 커밋 `6cbb676`
> 판정: **코드 배포 완료, 데이터 기능 운영 검증 미완료**. Firestore 할당량 초과가 해소되기 전에는 전체 시연을 완료로 표시하지 않는다.

## 현재 확인한 사실

- [x] GitHub `main`에 `6cbb676` 푸시
- [x] Render 대시보드에서 해당 커밋 **Live**, `/health` 200
- [x] Vercel 배포 상태 success, 운영 URL에서 새 `theme.js` 제공
- [x] 로컬 자동 테스트 19개 통과, `frontend/app.js`·`frontend/theme.js` 문법 확인
- [ ] 분석 데이터 정상 응답 (현재 `/api/data/ranking?period=13w&limit=5`는 `503 DATASTORE_QUOTA_EXCEEDED`)
- [ ] `analytics_snapshots/current` 원격 최초 생성·재사용 확인

## 배포 설정 확인

1. Render의 `ADMIN_API_KEY`, `GITHUB_TOKEN`, `OPENAI_API_KEY`, Firebase 서비스 계정 값과 `FIRESTORE_ENABLED=true`를 확인한다. 비밀값을 문서·브라우저·Git에 넣지 않는다.
2. `CORS_ORIGINS`에 실제 Vercel Frontend origin을 지정한다. Frontend `config.js`의 배포 Backend 주소는 `https://ai-assi-for-me.onrender.com`이다.
3. Firestore 할당량이 복구된 후 **한 번만** 랭킹을 호출해 분석 문서 생성 여부를 확인한다. 실패 중 반복 새로고침·수동 동기화는 피한다.
4. `/docs`·`/openapi.json` 및 Summary가 현재 배포에서도 응답하는지 다시 확인한다. `/health` 200만으로 데이터 저장소 정상 상태를 판단하지 않는다.

## 평가 시나리오 — 할당량 복구 후 실행

- [ ] 웹 URL, Swagger UI와 모바일/작은 화면 접속
- [ ] Ranking·Summary·Compare·Trends 응답과 기간 변경
- [ ] 기술 상세 52주 차트와 현재 누적 Star 표시
- [ ] 관리자 키로 Demo 데이터 추가 → Firestore `technology_data_manual` 확인 → 화면 목록 반영 → 삭제
- [ ] Summary 수치와 Chat 답변의 기간·근거 대조
- [ ] Chat 후속 질문, 대화 목록·불러오기, 다른 세션 접근 차단
- [ ] 라이트/다크 테마 전환 및 새로고침 후 유지
- [ ] 첫 접속 지연 안내, 관리자 키 없는 쓰기 요청 401, 허용하지 않은 origin의 CORS 동작
- [ ] 주간 동기화 후 분석 문서 갱신 및 Firestore 사용량 비교

로컬 자동 테스트: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. 화면 시연 순서는 `DEMO_SCENARIO.md`를 참고한다. 과거 2026-10-08의 성공 기록은 현재 운영 상태의 재검증을 대신하지 않는다.
