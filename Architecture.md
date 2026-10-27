# AI 기술 트렌드 레이더 — Architecture

> 기준 문서: `PRD.md` Final 1.0
> 상태: 구현 구조 및 제출 설명
> 목적: 개발자가 동일한 데이터 흐름·책임 분리·보안 경계를 기준으로 구현하기 위한 구조 문서

## 1. 시스템 목표

전체 10개 AI 기술 저장소의 GitHub 주별 Star 데이터를 수집·저장하고, 최근 13주 기준 주당 평균 신규 Star와 Momentum을 계산해 관심 기술 상위 5개를 제공한다. 사용자는 기술 상세 화면과 AI Chat에서 분석 근거를 확인한다.

금융 투자 판단이 아니라 학습 시간과 업무 리소스를 투자할 기술을 찾는 서비스다.

## 2. 전체 구성

```text
Frontend (Vanilla HTML/CSS/JavaScript)
  Dashboard · Detail · Chat
             │ HTTPS / JSON
             ▼
FastAPI Backend
  Router · Auth · Services · Analytics · AI Tools
       │              │              │
       ▼              ▼              ▼
   Firestore       GitHub API     OpenAI API
 weekly data      Star History   Chat/Tool calls
 snapshots
 conversations
```

배포 구성은 `Vercel Frontend → Render FastAPI Backend → Firestore/GitHub/OpenAI`다.

## 3. 책임 분리

### Frontend

- 랭킹·상세·차트·Chat 화면 렌더링
- 사용자 입력과 기간 선택 처리
- 첫 방문 시 256비트 `X-Session-Token` 생성 및 `localStorage` 저장
- 관리자 키는 저장하지 않고 현재 메모리 세션에서만 전달
- 통계 계산은 하지 않고 Backend 응답을 표시

### Backend Router

- HTTP 입력·출력과 상태 코드 관리
- Pydantic 입력 검증
- `X-Admin-Key`, `X-Session-Token` 검증
- Service 호출 후 JSON 응답 반환

라우터는 기능별로 `api_data.py`(수동 CRUD·목록·동기화), `analytics_api.py`(Summary·비교·랭킹·추세), `conversation_api.py`(대화 CRUD), `chat_api.py`(AI 질의), `export_api.py`(내보내기)로 나눈다. `main.py`는 등록·CORS·공통 오류 처리를 담당한다. HTTP 밖에서도 재사용할 계산은 `analytics.py`, 저장 구현은 `storage.py`와 `conversations.py`에 둔다.

### Data Service

- Firestore CRUD
- 중복 키 `repository + week_start_epoch + metric` 처리
- `source`, `source_type`, `analysis_eligible` 서버 강제
- GitHub 행 일반 수정·삭제 차단
- Firebase 환경변수가 완비되면 Firestore Adapter를 사용하고, 로컬 무자격증명 환경에서는 명시된 메모리 fallback을 사용

### Ingestion Service

- GitHub `stargazers/history` 페이지 순회
- `week`, `total`, `days` 응답 정규화
- `total`을 `weekly_new_stars`로 변환
- 진행 중인 주 제외
- 주 1회 자동 갱신과 보호된 수동 동기화 실행
- 현재 누적 Star는 별도 snapshot으로 저장

### Analytics Service

- `4w`, `13w`, `26w`, `52w` 완결 주 계산
- 주별 합계·평균·최대·최소 계산
- 직전 동일 기간과 Momentum 계산
- 10% 기준 상태 판정
- 데이터 부족·baseline 0 예외 처리
- 상위 5개 랭킹 계산

### AI/Tool Service

- 통계 계산은 Backend에서 수행
- Tool 결과만 OpenAI 답변의 수치 근거로 사용
- 다음 4개 Tool을 제공한다.
  - `get_technology_summary`
  - `compare_technologies`
  - `get_trend_changes`
  - `get_technology_history`

## 4. 데이터 모델

### `technology_data` / `technology_data_manual`

필수 필드:

`technology`, `repository`, `date`, `week_start_epoch`, `value`, `metric`, `source`, `source_type`, `analysis_eligible`, `collected_at`, `created_at`, `updated_at`

고정 정책:

- `metric=weekly_new_stars`
- GitHub 수집: `source=github`, `source_type=github_star_history`, `analysis_eligible=true`
- 수동 입력은 `technology_data_manual`에 저장: `source=manual_demo`, `source_type=manual_entry`, `analysis_eligible=false`
- 유일성: `repository + week_start_epoch + metric`
- 누락 주를 임의로 생성하지 않음

GitHub 원본과 사용자 Demo 행을 별도 컬렉션에 둬 수동 입력이 공식 분석값을 오염시키지 않게 한다. `GET /api/data`는 두 컬렉션을 함께 조회할 수 있지만 Summary·Ranking·Chat Tool은 GitHub 분석 행만 사용한다. `DataWritePayload`는 클라이언트 입력을 검증하고 출처 필드는 서버가 강제한다. `TechnologyData`는 저장·응답의 공통 형식을 검증한다.

### `technology_snapshots`

필드: `technology`, `repository`, `current_stargazer_count`, `collected_at`

현재 누적 Star 표시 전용이다. 주별 차트·Summary·Momentum·Ranking 계산에는 사용하지 않는다.

### `conversations`

필드: `id`, `title`, `messages`, `session_hash`, `created_at`, `updated_at`

- 토큰 원문은 브라우저 `localStorage`에만 저장
- 서버에는 SHA-256 `session_hash`만 저장
- 목록·조회·삭제·후속 채팅을 현재 세션으로 제한
- 다른 세션의 ID는 404
- 토큰 삭제 후 기존 대화 재접근 불가

## 5. 핵심 데이터 흐름

### 주간 수집

주 1회 scheduler 또는 Admin sync → GitHub history API page 1..N → 응답 정규화 → 진행 중 주 제외 → 중복 검사 → `technology_data` 저장 → snapshot 별도 저장

### 랭킹 조회

`GET /api/data/ranking?period=13w&limit=5` → `analysis_eligible=true` 필터 → 최근·직전 13주 계산 → 평균과 Momentum 계산 → 평균 내림차순·Momentum 보정 정렬 → 상위 5개와 근거 반환

### AI Chat

User message + session token → 이전 대화 최근 6개 메시지 조회 → OpenAI Tool 선택(또는 Gateway에서 Backend Tool 선택) → Backend arguments 검증 → Analytics/Firestore 실행 → Tool 결과 재전달 → 근거 기반 답변 → `session_hash`로 저장. AI 키가 없는 로컬 모드에서는 Backend Tool 결과를 결정론적으로 설명한다.

Frontend의 `activeConversationId`는 새 세션에서 `null`이고 첫 Chat 응답에서 발급된 ID로 바뀐다. 목록 버튼을 누르면 해당 ID로 저장 메시지를 불러온다. 데이터 관리 폼은 관리자 키와 입력값을 보내고 성공 시 목록을 다시 조회한다. 랭킹 카드를 누르면 Summary·GitHub 주별 행·Snapshot을 조회해 상세를 채운다.

Summary는 Chat과 독립된 API다. 기간 규칙을 바꾸려면 `analytics.py`의 `PERIOD_WEEKS`와 계산·테스트, `analytics_api.py`의 Query 허용값, `ai_tools.py`의 Tool schema, Frontend 기간 선택지를 함께 수정한다. 최근 30일처럼 달력 기준을 도입하려면 완결 주 기준과 다른 경계 규칙도 먼저 정해야 한다.

## 6. 보안 경계

- `ADMIN_API_KEY`는 Backend 환경변수에만 둔다.
- 관리자 키는 공개 JavaScript, HTML, localStorage, sessionStorage, 쿠키에 저장하지 않는다.
- 관리자가 실행 중 직접 입력하고 현재 메모리에서만 사용한다.
- 키 누락·불일치 시 쓰기·동기화를 수행하지 않고 401/403을 반환한다.
- Conversation 토큰은 관리자 키와 별개이며 localStorage에 저장한다.
- OpenAI·Firebase 자격증명은 Backend 환경변수로만 관리한다.
- Chat 입력 길이·모델·출력 토큰·rate limit을 Backend에서 제한한다.

## 7. API 경계

### v1 필수

- `POST /api/data`
- `GET /api/data`
- `PUT /api/data/{id}`
- `DELETE /api/data/{id}`
- `POST /api/data/sync/github` — Admin/Demo 권한 필요
- `GET /api/data/summary`
- `GET /api/data/compare`
- `GET /api/data/ranking`
- `GET /api/data/trends`
- `POST|GET|DELETE /api/conversations` — `X-Session-Token` 필요
- `GET /api/conversations/{id}` — `X-Session-Token` 필요
- `POST /api/chat` — `X-Session-Token` 필요

### 추가 구현

- `GET /api/export/csv`
- `GET /api/export/json`

## 8. 배포 구조

```text
Vercel Frontend
      │ HTTPS
      ▼
Render FastAPI Backend ─── Firestore
      ├── GitHub API
      └── OpenAI API
```

- 배포 전 CORS 허용 origin을 실제 Frontend 도메인으로 제한한다.
- Render 환경변수에 GitHub/OpenAI/Firebase/Admin 설정을 둔다.
- Vercel에는 Backend URL만 공개 설정한다.
- 관리자 키와 외부 API 비밀값은 Vercel 번들에 넣지 않는다.

## 9. Phase 0 반영 사항

- 10개 저장소 모두 GitHub 공식 Star History API 접근 가능
- 모두 104주 이상 확보
- `week`, `total`, `days` 구조 확인
- `total → weekly_new_stars` 변환 가능
- Microsoft Agent Framework는 76주로 기준 미충족하여 Dify로 교체
- 검증 상세: `DATA_VALIDATION.md`
- 대체 결정·파싱 버그 수정: `DECISIONS.md`

## 10. 결정 완료

구현 전 결정사항은 모두 `DECISIONS.md`에 근거·대안·트레이드오프·결과를 기록했다.

- Chart: Vanilla SVG/CSS bar chart
- OpenAI model: `OPENAI_MODEL` 환경변수, 기본값 `gpt-4o-mini`
- MCP: 프로젝트 내부 경량 JSON-RPC Server
- Chat: 시간당 20회, 입력 2,000자
- MCP 대체안: 구현 불가 시 GPT Actions 검토

