# AI Tech Trend Radar

학습 시간과 업무 리소스를 투자할 가치가 있는 AI 기술을 찾기 위한 개인용 기술 트렌드 레이더입니다. 금융 투자 조언을 제공하지 않습니다.

## 1. 이 프로젝트가 하는 일

GitHub Star History를 매주 수집하고, 최근 완결 주의 `weekly_new_stars`를 분석합니다.

1. 10개 AI 기술 저장소의 Star 이력을 수집합니다.
2. 진행 중인 주를 제외하고 주별 신규 Star를 계산합니다.
3. 최근 `4w·13w·26w·52w`와 직전 동일 기간을 비교합니다.
4. 주당 평균 신규 Star와 Momentum 10%를 이용해 상위 5개를 보여줍니다.
5. 기술 비교·상세 차트·Export·AI Chat을 제공합니다.

## 2. 초보자용 전체 진행 순서

### 준비물

- Windows PowerShell
- Python 3.11 이상
- Git
- GitHub 계정과 Personal Access Token
- Firebase 프로젝트와 Service Account
- Render·Vercel 계정(공개 배포 시)
- AI Chat을 사용하려면 OpenAI 호환 API 키

### 2.1 저장소 받기

```powershell
git clone https://github.com/bomigrace-byte/ai-assi-for-me.git
Set-Location .\ai-assi-for-me
```

### 2.2 Python 환경 만들기

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`(.venv)` 표시가 없어도 `.venv\Scripts\python.exe`를 직접 호출하면 됩니다.

### 2.3 환경변수 파일 만들기

```powershell
Copy-Item .env.example .env
notepad .env
```

`.env`에는 실제 값을 입력하되 Git에 커밋하지 않습니다.

```text
GITHUB_TOKEN=GitHub_TOKEN
ADMIN_API_KEY=관리자용_비밀키
FIREBASE_PROJECT_ID=Firebase_프로젝트_ID
FIREBASE_CLIENT_EMAIL=서비스계정_이메일
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIRESTORE_ENABLED=true

# OpenAI 또는 기관 OpenAI 호환 API를 사용할 때만 입력
OPENAI_API_KEY=기관_API_KEY
OPENAI_BASE_URL=https://copa.codyssey.kr/v1
OPENAI_MODEL=gpt-5-mini
```

관리자 키·GitHub 토큰·Firebase 키·AI API 키는 브라우저 코드나 GitHub 저장소에 넣지 않습니다.

### 2.4 Firestore 연결 확인

```powershell
.\.venv\Scripts\python.exe tools\verify_firestore.py
```

성공 결과:

```text
FIRESTORE_REMOTE_SMOKE_OK
```

이 테스트는 데이터를 지우지 않는 원격 연결 확인입니다. Firebase Console에서 `technology_data`, `technology_data_manual`, `technology_snapshots`, `conversations` 컬렉션이 사용되는지 확인합니다.

### 2.5 Backend 실행

터미널 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

확인:

- 상태 확인: <http://127.0.0.1:8000/health>
- API 문서: <http://127.0.0.1:8000/docs>

`/health` 응답이 `{"status":"ok"}`이면 Backend가 실행 중입니다.

### 2.6 Frontend 실행

터미널 2:

```powershell
py -m http.server 3000 --directory frontend
```

브라우저에서 <http://127.0.0.1:3000>을 엽니다.

### 2.7 GitHub 데이터 동기화

관리자 키를 PowerShell에서 직접 입력해 실행합니다. 키를 명령 기록이나 채팅에 공개하지 마세요.

```powershell
$admin = Read-Host "ADMIN_API_KEY"
Invoke-WebRequest `
  -Uri http://127.0.0.1:8000/api/data/sync/github `
  -Method Post `
  -Headers @{ 'X-Admin-Key' = $admin }
```

성공하면 10개 저장소의 주별 데이터와 현재 누적 Star Snapshot이 Firestore에 저장됩니다.

### 2.8 화면에서 확인할 기능

1. 상위 5개 랭킹 확인
2. 기간을 `4w·13w·26w·52w`로 변경
3. 두 기술 비교
4. 랭킹 카드를 눌러 주별 차트와 Snapshot 확인
5. CSV/JSON Export
6. 새 익명 세션에서 AI Chat 질문

## 3. 실제 배포

### Render Backend

Render에서 GitHub 저장소를 연결하고 다음을 사용합니다.

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Health Check: /health
```

Render 환경변수에는 로컬 `.env`와 같은 서버 전용 값을 입력합니다. 특히 `FIRESTORE_ENABLED=true`, `CORS_ORIGINS`에 Vercel 주소를 설정합니다.

### Vercel Frontend

Vercel 프로젝트의 Root Directory를 `frontend`로 설정하고 배포합니다. `frontend/config.js`의 `API_BASE`는 Render Backend 주소여야 합니다.

현재 배포 주소:

- Frontend: <https://ai-assi-for-me-frontend.vercel.app/>
- Backend: <https://ai-assi-for-me.onrender.com>

### 주간 자동 동기화

`.github/workflows/weekly-github-sync.yml`이 매주 월요일 11:00(KST)에 보호된 동기화 API를 호출합니다.

GitHub 저장소의 `Settings → Secrets and variables → Actions → Secrets`에 다음 Repository secret을 등록합니다.

- `RENDER_BACKEND_URL`: `https://ai-assi-for-me.onrender.com`
- `ADMIN_API_KEY`: Render에 설정한 관리자 키

Actions의 `Weekly GitHub Star Sync → Run workflow`로 수동 실행할 수도 있습니다.

## 4. 데이터·분석 규칙

- 초기 추적 저장소: 10개
- 최소 분석 범위: 저장소별 완결 104주
- 주별 지표: `weekly_new_stars`
- 현재 누적 Star: `technology_snapshots`에 별도 저장
- Momentum 임계값: 10%
- 수동 Demo 행: `source=manual_demo`, `analysis_eligible=false`
- GitHub 행: 일반 수정·삭제 금지
- 중복 기준: `repository + week_start_epoch + metric`

## 5. 주요 API

| 목적 | 경로 |
|---|---|
| 상태 확인 | `GET /health` |
| 랭킹 | `GET /api/data/ranking?period=13w&limit=5` |
| 기술 요약 | `GET /api/data/summary?technology=LangGraph&period=13w` |
| 기술 비교 | `GET /api/data/compare?technologies=LangGraph,LangChain&period=13w` |
| 추세 변화 | `GET /api/data/trends?technology=LangGraph&period=13w` |
| Export | `GET /api/export/json`, `GET /api/export/csv` |
| GitHub 동기화 | `POST /api/data/sync/github` (관리자 키 필요) |
| Chat | `POST /api/chat` (`X-Session-Token` 필요) |
| MCP | `python -m backend.mcp_server` |

## 6. AI Chat 동작 방식

기관 OpenAI 호환 Gateway를 사용할 때는 Backend가 먼저 신뢰할 수 있는 분석 수치를 계산하고, AI API에는 결과를 문장으로 설명하도록 요청합니다. 따라서 AI가 임의로 Star 수나 Momentum을 계산하지 않습니다.

기관 API가 없으면 `OPENAI_API_KEY`를 비워 로컬 결정론적 답변으로 동작시킬 수 있습니다. OpenAI Function Calling을 직접 사용할 수 있는 API를 연결하면 4개 Tool을 사용할 수 있습니다.

기관 API 오류가 발생하면 다음을 확인합니다.

- Base URL에 `/v1`이 포함됐는지
- 모델명이 기관에서 허용한 이름인지
- API 키 앞뒤 공백·따옴표가 없는지
- 기관 API가 `Authorization: Bearer` 인증을 사용하는지
- Render가 최신 환경변수로 재배포됐는지

## 7. 검증 명령

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall backend
node --check frontend/app.js
```

대표 API 확인:

```powershell
curl.exe https://ai-assi-for-me.onrender.com/health
curl.exe "https://ai-assi-for-me.onrender.com/api/data/ranking?period=13w&limit=5"
```

## 8. 이번 미션에서 배울 핵심 개념

### 데이터 파이프라인

외부 API 응답을 그대로 화면에 쓰지 않고, `week·total·days`를 검증한 뒤 `weekly_new_stars`라는 분석용 데이터로 변환합니다. 수집·정규화·저장·분석을 분리하는 기본적인 데이터 파이프라인입니다.

### 시계열 분석

현재 누적 Star와 주별 신규 Star는 다른 지표입니다. 최근 13주 평균과 직전 13주 평균을 비교해 Momentum을 계산하고, 진행 중인 주는 제외합니다.

### 데이터 무결성과 Idempotency

`repository + week_start_epoch + metric`을 중복 키로 사용해 같은 데이터를 여러 번 수집해도 행이 중복되지 않도록 합니다. 재실행 가능한 수집 작업의 핵심 개념입니다.

### 서버 신뢰 경계

클라이언트가 `source`, `source_type`, `analysis_eligible`을 보내더라도 서버가 실제 값을 결정합니다. GitHub 행을 일반 수정·삭제하지 못하게 해 데이터 오염을 막습니다.

### 세션 격리

로그인 없이도 브라우저별 256비트 세션 토큰을 만들고, 서버에는 원문이 아닌 `session_hash`만 저장합니다. 다른 브라우저의 Conversation ID는 접근할 수 없습니다.

### Backend와 Frontend 분리 배포

FastAPI는 Render, 정적 HTML/CSS/JavaScript는 Vercel에 배포합니다. CORS, 환경변수, 공개 키와 비밀 키의 차이를 실제 서비스 구조에서 배웁니다.

### AI와 결정론적 계산의 역할 분리

AI는 설명을 자연스럽게 만드는 역할을 하고, Star 수·평균·Momentum·랭킹은 Backend가 계산합니다. 이 구조가 AI 답변의 근거성과 재현성을 높입니다.

### 운영 자동화

GitHub Actions가 주기적으로 보호된 API를 호출합니다. timeout, 재시도, Secret 관리, 로그 확인처럼 개발 완료 후 필요한 운영 개념도 포함합니다.

## 9. 검증 결과

2026-10-08 기준 최종 검증 결과입니다.

- Firestore 원격 연결: `FIRESTORE_REMOTE_SMOKE_OK`
- 10개 저장소 데이터 적재 및 Snapshot 저장: 성공
- Render health·OpenAPI·Ranking·Summary·Compare·Export: 모두 `200`
- Vercel Top 5 카드·기간 변경·비교·상세 차트·Conversation: 성공
- 기관 `gpt-5-mini` 기반 AI Chat: 성공
- GitHub Actions 주간 동기화: 성공(약 9분 49초)

## 10. 참고 문서

- [PRD.md](PRD.md): 제품 요구사항
- [Architecture.md](Architecture.md): 시스템 구조
- [DATA_VALIDATION.md](DATA_VALIDATION.md): 데이터 검증 결과
- [DECISIONS.md](DECISIONS.md): 주요 결정 기록
- [TASK.md](TASK.md): Phase별 실행 체크리스트
- [AI_USAGE_LOG.md](AI_USAGE_LOG.md): AI 활용 기록
