# AI Tech Trend Radar

학습 시간과 업무 리소스를 투자할 가치가 있는 AI 기술을 찾기 위한 개인용 기술 트렌드 레이더입니다. 금융 투자 조언을 제공하지 않습니다.

## 최종 서비스 접속

2026-10-28 기준 읽기 절약 커밋 `2dabf6b`이 Render·Vercel에 배포됐습니다. 운영 `/health`, 랭킹, 요약, 홈페이지 랭킹·상세·비교, 임시 세션 Chat 및 대화 저장·불러오기를 확인했습니다. 다만 주간 동기화의 실제 증분 실행과 장기 사용량은 다음 정기 실행 후 검증해야 합니다.

- **홈페이지:** <https://ai-assi-for-me-frontend.vercel.app/>
- **Backend 상태 확인:** <https://ai-assi-for-me.onrender.com/health>
- **Backend API 문서:** <https://ai-assi-for-me.onrender.com/docs>
- **JSON 데이터 Export:** <https://ai-assi-for-me.onrender.com/api/export/json?metric=weekly_new_stars>
- **CSV 데이터 Export:** <https://ai-assi-for-me.onrender.com/api/export/csv?metric=weekly_new_stars>

일반 사용자는 홈페이지 링크를 열면 됩니다. `/health`는 서버 기동만 확인하며 Firestore 정상 작동을 보장하지 않습니다. `/docs`는 API 문서, Export 주소는 데이터 저장소가 사용 가능할 때만 확인합니다.

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
- 자연어 AI 답변을 사용하려면 OpenAI 호환 API 키(키가 없으면 Backend 계산 결과의 결정론적 설명으로 동작)

### 2.1 저장소 받기

```powershell
git clone https://github.com/bomigrace-byte/ai-assi-for-me.git
Set-Location .\ai-assi-for-me
```

### 2.2 Python 환경 만들기

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
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

이 테스트는 데이터를 지우지 않는 원격 연결 확인입니다. Firebase Console에서 `technology_data`, `technology_data_manual`, `technology_snapshots`, `conversations` 컬렉션이 사용되는지 확인합니다. `analytics_snapshots/current`는 첫 공개 분석 요청 또는 동기화 완료 후 생성되므로, 최초 연결 테스트만으로는 존재하지 않을 수 있습니다.

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
.\.venv\Scripts\python.exe tools\serve_frontend.py
```

브라우저에서 <http://127.0.0.1:3000>을 엽니다.

로컬 미리보기 서버는 배포 Backend API를 같은 출처로 전달해 로컬 브라우저의 CORS 제한을 해결합니다. 랭킹·상세·비교뿐 아니라 Chat·대화 불러오기도 사용할 수 있습니다. Chat 메시지와 관리자 키를 입력한 평가용 데이터 변경은 배포 Backend로 전달되고, 대화와 데이터는 원격 Firestore에 저장됩니다. GitHub 동기화 경로는 로컬 미리보기에서 허용하지 않습니다. 로컬에서 모든 데이터를 독립적으로 운영하려면 별도의 Backend 실행·Firebase 및 AI 비밀값 설정이 필요합니다.

로컬 Backend 코드를 직접 확인하려면 Frontend 서버를 시작하기 전에 PowerShell에서 `$env:PREVIEW_BACKEND_URL = "http://127.0.0.1:8000"`을 설정합니다. 이때 랭킹은 로컬 Backend에 저장된 데이터가 있어야 표시됩니다.

### 2.7 GitHub 데이터 동기화

관리자 키를 PowerShell에서 직접 입력해 실행합니다. 키를 명령 기록이나 채팅에 공개하지 마세요.

```powershell
$admin = Read-Host "ADMIN_API_KEY"
Invoke-WebRequest `
  -Uri http://127.0.0.1:8000/api/data/sync/github `
  -Method Post `
  -Headers @{ 'X-Admin-Key' = $admin }
```

성공하면 10개 저장소의 주별 데이터와 현재 누적 Star Snapshot이 Firestore에 저장되고, 공개 분석용 `analytics_snapshots/current`가 갱신됩니다. 기존 구현은 동기화 중 많은 문서를 다시 읽고 쓰므로 할당량이 충분한지 먼저 확인하세요.

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

### Firestore 읽기 절약

공개 랭킹·요약·비교·추세 및 Chat의 분석 Tool은 원본 `technology_data` 전체를 매번 읽지 않습니다. 동기화가 끝나면 네 기간(4/13/26/52주)의 분석 결과를 계산해 `analytics_snapshots/current` 한 문서에 저장합니다. 일반 요청은 이 문서를 읽고 서버 메모리에 10분간 캐시합니다. 문서가 없거나 형식이 맞지 않으면 원본 전체를 자동으로 읽지 않고 `503 ANALYTICS_NOT_READY`를 반환합니다. 없는 문서 조회도 1분간 캐시해 반복 조회를 줄입니다. 기술 상세의 주별 기록과 누적 Star는 해당 기술로 필터링해 조회합니다. 수동 Demo 데이터는 분석 문서에 포함하지 않습니다.

대화 목록은 전체 `conversations`가 아닌 현재 익명 세션의 문서만 조회합니다. GitHub 동기화는 기존 분석 문서의 마지막 완결 주 이후 행만 저장하고, 새로운 행이 없으면 분석 문서를 재계산하지 않습니다. 동기화 엔드포인트의 중복 실행은 같은 서버 프로세스 안에서 차단하고 GitHub Actions의 중복 작업도 대기시킵니다. 분석 문서 조회·원본 전체/기술별 조회의 예상 문서 수와 동기화 저장 수는 서버 로그에 남깁니다. 이는 Firestore의 실제 청구 수치와 완전히 같지 않으므로 Firebase 사용량 화면과 대조해야 합니다. 최초 적재·전체 데이터 목록/내보내기는 여전히 많은 Firestore 읽기/쓰기를 사용할 수 있습니다. 여러 서버 프로세스 간 동기화 중복 차단은 아직 구현되지 않았습니다.

### Star란?

GitHub에서 사용자가 저장소에 보내는 관심 표시입니다. 일반적인 소셜 서비스의 좋아요와 비슷하지만, 개발자가 해당 오픈소스 프로젝트를 북마크하거나 관심 프로젝트로 표시하는 의미로도 사용합니다.

따라서 Star가 많다는 것은 현재까지 많은 관심을 받았다는 뜻이지, 기술의 품질이나 미래 성공을 보장한다는 뜻은 아닙니다.

### weekly_new_stars란?

특정 주에 새로 추가된 Star의 개수입니다.

예를 들어 누적 Star가 다음과 같다면:

```text
1주차 시작: 10,000 Star
2주차 시작: 10,250 Star
```

해당 주의 `weekly_new_stars`는 `250`입니다. 이 프로젝트는 현재 누적 Star 자체가 아니라, 주별 신규 Star의 흐름을 분석합니다.

### Momentum 10%란?

최근 기간의 주당 평균 신규 Star가 직전 동일 기간보다 얼마나 변했는지를 나타내는 지표입니다.

```text
Momentum = (최근 기간 평균 - 직전 기간 평균) / 직전 기간 평균 × 100
```

예를 들어:

```text
직전 13주 평균: 500 Star/주
최근 13주 평균: 550 Star/주
Momentum: (550 - 500) / 500 × 100 = +10%
```

이 프로젝트에서는 변화율을 다음처럼 읽습니다.

- `+10% 이상`: 성장 속도가 뚜렷하게 증가한 상태
- `-10% 이하`: 성장 속도가 뚜렷하게 둔화한 상태
- `-10% 초과 ~ +10% 미만`: 큰 변화가 없는 상태

Momentum 10%는 투자 수익률이나 금융 투자 신호가 아닙니다. 학습 시간과 업무 리소스를 어느 기술에 더 배분할지 판단하기 위한 참고 지표입니다. 직전 기간 평균이 0이면 `insufficient_baseline`, 완결 주가 부족하면 `insufficient_data`로 표시합니다.

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

`GET /api/data/summary?technology=LangGraph&period=13w`는 Backend 분석 결과를 독립적으로 제공합니다. 화면의 상세 카드와 Chat Tool이 같은 분석 규칙을 재사용하며, AI를 호출하지 않아도 수치와 상태를 검증할 수 있습니다. 대화는 익명 세션별 `conversations` 문서에 사용자·AI 메시지 배열로 저장합니다. Chat 답변이 성공한 뒤 질문·답변을 한 번에 저장하므로 실패한 요청은 빈 대화를 남기지 않습니다. 화면의 “새 대화”는 같은 익명 세션 안에서 새 대화를 시작하며 이전 목록을 유지합니다. 목록에서 선택하면 저장된 내용을 불러옵니다. 후속 질문에는 최근 6개 메시지를 각 600자 이내로 잘라 AI에 전달하고, 기술명을 생략하면 이전 사용자 질문의 기술명을 이어받습니다.

이 컨텍스트 주입은 답변에 분석 근거를 주고 후속 질문을 이해하는 데 도움이 됩니다. 반면 메시지와 분석 결과가 길어질수록 토큰 비용·지연이 증가하고, 사용자 입력이나 외부 데이터에 포함된 지시문이 AI를 오도할 수 있습니다. 따라서 전달하는 기록을 제한하고, 시스템 지시에서 대화·Tool 결과를 데이터로 취급하며, 분석 수치는 Backend가 계산합니다. 이 조치가 프롬프트 주입을 완전히 막지는 못하므로 답변의 수치와 기간은 Summary API 결과와 대조할 수 있게 합니다.

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
node --check frontend/theme.js
```

대표 API 확인:

```powershell
curl.exe https://ai-assi-for-me.onrender.com/health
curl.exe "https://ai-assi-for-me.onrender.com/api/data/ranking?period=13w&limit=5"
curl.exe "https://ai-assi-for-me.onrender.com/api/data/summary?technology=LangGraph&period=13w"
```

실제 평가 전에는 배포된 `/docs`에서 Summary 경로를 확인하고, 관리자 키로 Demo 행을 추가해 Firestore `technology_data_manual` 저장과 화면 목록 반영을 확인하세요. 이어서 Chat 질문·대화 불러오기·작은 화면 사용을 브라우저에서 확인해야 합니다. 이 절차에는 실제 배포 자격증명이 필요하므로 로컬 자동 테스트와 별개입니다.

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

### 입력 검증과 표시

Pydantic이 데이터 값·저장소 형식·Chat 길이(최대 2,000자)를 검사합니다. 서버는 수동 입력을 분석 대상에서 제외하고, Chat 요청을 세션별 시간당 20회로 제한합니다. 화면은 대화·Demo 입력을 HTML 문자로 이스케이프해 스크립트로 해석되지 않도록 합니다. 추가 필터가 필요하면 `backend/policies.py`의 입력 스키마와 `backend/chat_api.py`의 Chat 정책을 수정합니다.

### 첫 접속 지연

Backend가 절전 상태에서 시작하면 첫 조회가 늦어질 수 있습니다. 화면은 8초 뒤 “서버가 시작 중일 수 있습니다”라는 안내와 재시도 방법을 표시합니다. GitHub 데이터는 주간 자동 동기화로 갱신하며, 이 작업은 서버를 영구적으로 깨워 두는 기능은 아닙니다. 일정한 첫 접속 속도가 필요해지면 호스팅 플랜 조정이나 호스팅 정책에 맞는 프리히트를 별도로 검토합니다.

### Backend와 Frontend 분리 배포

FastAPI는 Render, 정적 HTML/CSS/JavaScript는 Vercel에 배포합니다. CORS, 환경변수, 공개 키와 비밀 키의 차이를 실제 서비스 구조에서 배웁니다.

### AI와 결정론적 계산의 역할 분리

AI는 설명을 자연스럽게 만드는 역할을 하고, Star 수·평균·Momentum·랭킹은 Backend가 계산합니다. 이 구조가 AI 답변의 근거성과 재현성을 높입니다.

### 운영 자동화

GitHub Actions가 주기적으로 보호된 API를 호출합니다. timeout, 재시도, Secret 관리, 로그 확인처럼 개발 완료 후 필요한 운영 개념도 포함합니다.

## 9. 검증 결과

아래 성공 항목은 **2026-10-08 당시 검증 기록**이며, 현재 정상 작동을 뜻하지 않습니다.

- Firestore 원격 연결: `FIRESTORE_REMOTE_SMOKE_OK`
- 10개 저장소 데이터 적재 및 Snapshot 저장: 성공
- Render health·OpenAPI·Ranking·Summary·Compare·Export: 모두 `200`
- Vercel Top 5 카드·기간 변경·비교·상세 차트·Conversation: 성공
- 기관 `gpt-5-mini` 기반 AI Chat: 성공
- GitHub Actions 주간 동기화: 성공(약 9분 49초)

**2026-10-28 운영 재검증:** `analytics_snapshots/current` 문서가 존재하며 `generated_at`은 `2026-10-28T11:40:47Z`입니다. 커밋 `2dabf6b` 배포 후 Backend `/health`, 랭킹, Dify 요약은 `200`이었습니다. 운영 브라우저에서 상위 5개 카드, Dify 상세, Dify–Ollama 비교, 대화 목록을 확인했습니다. 별도 임시 세션의 Chat 답변·대화 저장·불러오기도 성공했고 테스트 대화는 삭제했습니다. Render 로그에는 첫 분석 요청의 스냅샷 문서 추정 읽기 1건이 남았고 뒤이은 랭킹·요약 요청에는 추가 스냅샷 읽기 로그가 없었습니다. Dify 상세의 원본 기술별 조회는 주간 문서 185건을 읽었습니다. 이 로그는 청구 사용량의 완전한 측정이 아닙니다. 이전 5만 회 소진 원인은 확정하지 않았으며 실제 증분 동기화·장기 사용량·모바일 전체 흐름은 미검증입니다. 전체 Export·필터 없는 목록은 여전히 많은 읽기를 유발할 수 있으므로 반복 호출을 피하세요.

## 10. 참고 문서

- [PRD.md](PRD.md): 제품 요구사항
- [Architecture.md](Architecture.md): 시스템 구조
- [DATA_VALIDATION.md](DATA_VALIDATION.md): 데이터 검증 결과
- [DECISIONS.md](DECISIONS.md): 주요 결정 기록
- [TASK.md](TASK.md): Phase별 실행 체크리스트
- [AI_USAGE_LOG.md](AI_USAGE_LOG.md): AI 활용 기록
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md): 현재 배포 확인·미검증 항목
- [DEMO_SCENARIO.md](DEMO_SCENARIO.md): 할당량 복구 후 재검증 순서
- [PRD_AI_Tech_Trend_Radar_v0.3.md](PRD_AI_Tech_Trend_Radar_v0.3.md), [PRD_AI_Tech_Trend_Radar_v0.4.md](PRD_AI_Tech_Trend_Radar_v0.4.md): 과거 설계 보존본(현재 구현 기준 아님)
