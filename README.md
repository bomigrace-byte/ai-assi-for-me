# AI 기술 트렌드 레이더

학습 시간과 업무 리소스를 투자할 가치가 있어 계속 지켜볼 AI 기술을 찾는 개인용 MVP입니다. 금융 투자 조언을 제공하지 않습니다.

## 빠른 실행

Windows PowerShell 기준:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

다른 터미널에서 Frontend를 실행합니다. `frontend/config.js`는 로컬 Backend 주소를 기본값으로 사용합니다.

```powershell
py -m http.server 3000 --directory frontend
```

브라우저에서 <http://127.0.0.1:3000>을 열고, API 문서는 <http://127.0.0.1:8000/docs>에서 확인합니다. Vercel 배포 전에는 `frontend/config.js`의 `API_BASE`를 Render Backend 주소로 변경합니다.

## 환경변수

`.env.example`을 `.env`로 복사해 사용합니다. `ADMIN_API_KEY`, `GITHUB_TOKEN`, `OPENAI_API_KEY`, Firebase 자격증명은 Backend 환경변수에만 둡니다. 관리자 키는 UI에서 실행 중 직접 입력하며 브라우저 저장소·쿠키·번들에 저장하지 않습니다.

`OPENAI_API_KEY`가 없으면 로컬 검증용 결정론적 Backend Tool 응답을 사용합니다. 키가 있으면 `OPENAI_MODEL`로 지정한 모델이 Function Calling을 수행하고, 수치·판정은 Backend Tool 결과만 근거로 답합니다.

## 데이터와 동기화

- 초기 추적 저장소: 10개
- 최소 분석 범위: 저장소별 완결 104주
- 분석 지표: `weekly_new_stars`
- 현재 누적 Star: `technology_snapshots`에 별도 저장
- 자동 갱신: 주 1회 필수
- 수동 동기화: `POST /api/data/sync/github` (관리자 키 필요)
- 수동 데모 행: `analysis_eligible=false`이며 분석에서 제외

### Firestore 연결

`FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`가 모두 있으면 Backend가 Firebase Admin SDK로 Firestore를 사용합니다. 셋 중 하나라도 없으면 로컬 개발용 메모리 fallback을 사용합니다. 운영 Render에서는 `FIRESTORE_ENABLED=true`로 설정해 자격증명이 빠졌을 때 조용히 fallback하지 않도록 합니다. Service Account JSON과 private key는 저장소나 채팅에 올리지 않습니다.

실제 원격 연결 후에는 `technology_data`, `technology_data_manual`, `technology_snapshots`, `conversations` Collection 생성·조회가 되는지 Firebase Console과 API 양쪽에서 확인합니다.

원격 자격증명을 `.env`에 넣은 뒤 다음 비파괴 테스트를 실행할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe tools\verify_firestore.py
```

실제 데이터 검증 결과는 [DATA_VALIDATION.md](DATA_VALIDATION.md), 설계는 [Architecture.md](Architecture.md), 결정 기록은 [DECISIONS.md](DECISIONS.md), 실행 체크리스트는 [TASK.md](TASK.md)에 있습니다.

## 주요 API

| 목적 | 경로 |
|---|---|
| 랭킹 | `GET /api/data/ranking?period=13w&limit=5` |
| 기술 요약 | `GET /api/data/summary?technology=LangGraph&period=13w` |
| 기술 비교 | `GET /api/data/compare?technologies=LangGraph,LangChain&period=13w` |
| 추세 변화 | `GET /api/data/trends?technology=LangGraph&period=13w` |
| Export | `GET /api/export/json`, `GET /api/export/csv` |
| Chat | `POST /api/chat` (`X-Session-Token` 필요) |
| MCP | `python -m backend.mcp_server` |

## 검증

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall backend
node --check frontend/app.js
```

MCP는 stdio JSON-RPC의 `initialize`, `tools/list`, `tools/call`을 검증하고, 실제 GitHub 104주 검증은 `tools/validate_104_load.py`를 사용합니다. 외부 배포 시 Render Backend의 CORS에 실제 Vercel origin만 허용하고, Vercel에는 공개 가능한 Backend URL만 설정합니다.
