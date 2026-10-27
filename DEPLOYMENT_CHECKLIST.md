# 배포 및 제출 확인

README에는 2026-10-08 Render/Vercel 배포 검증이 기록되어 있습니다. 이 문서는 현재 확인해야 할 항목을 정리합니다. 2026-10-27 로컬 코드 보완은 아직 배포 상태를 증명하지 않습니다.

## 배포 설정

1. Render에 `ADMIN_API_KEY`, `GITHUB_TOKEN`, `OPENAI_API_KEY`, Firebase 서비스 계정 값을 Secret으로 둡니다. `FIRESTORE_ENABLED=true`를 확인합니다.
2. `CORS_ORIGINS`에 실제 Vercel Frontend origin을 지정합니다. FastAPI의 `backend/main.py`가 이 값을 읽습니다.
3. Vercel `frontend/config.js`의 `API_BASE`가 Render Backend 주소인지 확인합니다. 비밀 키는 Frontend에 넣지 않습니다.
4. 이번 로컬 변경을 배포한 뒤 `/health`, `/docs`, `/openapi.json`과 `/api/data/summary?technology=LangGraph&period=13w`의 응답을 확인합니다.

## 평가 시나리오

- [ ] 웹 URL과 Swagger UI 접속
- [ ] 관리자 키로 Demo 데이터 추가 → Firestore `technology_data_manual` 확인 → 화면 목록 반영 → 삭제
- [ ] Summary 수치와 Chat 답변의 기간·근거 대조
- [ ] Chat 후속 질문, 대화 목록·불러오기, 다른 세션 접근 차단 확인
- [ ] 작은 화면에서 랭킹·데이터 관리·Chat 사용 확인
- [ ] 첫 접속 지연 시 안내 문구와 재시도 확인
- [ ] 관리자 키 없는 쓰기 요청 401, 허용하지 않은 origin의 CORS 동작 확인

로컬 자동 테스트: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.
배포 후 수동 시연 순서는 `DEMO_SCENARIO.md`도 참고합니다. 체크박스는 실제 운영 환경에서 다시 확인한 뒤 표시합니다.
