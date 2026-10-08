# AI 기술 트렌드 레이더 — TASK

> 기준 문서: `PRD.md` Final 1.0  
> 목적: 세션 간 진행 상황을 공유하고 다음 작업자가 즉시 이어서 개발할 수 있도록 관리하는 실행 문서  
> 상태: `[ ]` 미착수 · `[-]` 진행 중 · `[x]` 완료 · `[!]` 차단/결정 필요

## 0. 전체 진행 현황

### Phase 0 — Data Spike 및 데이터 검증
- [x] **0.1** 10개 추적 저장소 목록과 식별자 확정
- [x] **0.2** 10개 저장소의 GitHub Star History 접근 가능 여부 확인
- [x] **0.3** 저장소별 최소 104개 완결 주 확보 가능 여부 확인
- [x] **0.4** `week`·`total`·`days` 구조와 의미 확인 (10개 저장소)
- [x] **0.5** `weekly_new_stars` 변환 로직 검증 (10개 저장소)
- [x] **0.6** 결과를 `DATA_VALIDATION.md`에 기록
- [x] **0.7** 실패 저장소의 대체 후보와 결정 사유 기록

### Phase 1 — Scaffold 및 아키텍처
- [x] **1.1** `Architecture.md` 작성 및 PRD 대조
- [x] **1.2** Backend/Frontend 디렉터리 생성
- [x] **1.3** Python 환경과 의존성 파일 구성
- [x] **1.4** FastAPI 기본 실행 및 `/docs` 확인
- [x] **1.5** 환경변수 템플릿과 비밀정보 취급 규칙 작성
- [x] **1.6** CORS·공통 오류 응답·기본 로깅 구성

### Phase 2 — Firestore 데이터 모델 및 Admin 보호
- [x] **2.1** `technology_data` 데이터 모델 구현
- [x] **2.2** `technology_snapshots` 데이터 모델 구현
- [x] **2.3** 필수 필드와 중복 키 구현
- [x] **2.4** `source`·`source_type`·`analysis_eligible` 서버 강제 규칙 구현
- [x] **2.5** GitHub 행 일반 수정·삭제 거부 구현
- [x] **2.6** `manual_demo` 행 CRUD 구현
- [x] **2.7** `X-Admin-Key`와 `ADMIN_API_KEY` 검증 구현
- [x] **2.8** 관리자 키를 브라우저 저장소·번들·쿠키에 저장하지 않도록 구현
- [x] **2.9** CRUD Swagger 테스트 작성

### Phase 3 — GitHub 수집 및 데이터 적재
- [x] **3.1** GitHub Star History 수집 서비스 구현
- [x] **3.2** API 응답을 주별 `weekly_new_stars`로 변환
- [x] **3.3** 진행 중인 주 제외 규칙 구현
- [x] **3.4** 중복 제거와 재수집 idempotency 구현
- [x] **3.5** `source=github`, `analysis_eligible=true` 서버 저장
- [x] **3.6** 현재 누적 Star snapshot 수집·저장·조회 구현
- [x] **3.7** 주 1회 자동 갱신 작업 구성 (v1 필수)
- [x] **3.8** 보호된 `/api/data/sync/github` 수동 동기화 API 구현
- [x] **3.9** 10개 저장소 × 104주 데이터 적재 및 검증

### Phase 4 — Analytics 및 관심 기술 랭킹
- [x] **4.1** 기간 규칙 `4w·13w·26w·52w` 구현
- [x] **4.2** 주별 합계·평균·최대·최소 계산
- [x] **4.3** 직전 동일 기간 계산
- [x] **4.4** Momentum 계산과 10% 판정 구현
- [x] **4.5** `previous_avg == 0` 예외 처리
- [x] **4.6** 관측 주 부족 상태 `insufficient_data` 처리
- [x] **4.7** snapshot과 주별 분석 지표 분리 검증
- [x] **4.8** 상위 5개 랭킹 API 구현
- [x] **4.9** 주당 평균 신규 Star 우선·Momentum 보정 정렬 구현
- [x] **4.10** 분석 단위 테스트 작성

### Phase 5 — Backend API 및 검증
- [x] **5.1** Summary API 구현
- [x] **5.2** Compare API 구현
- [x] **5.3** Ranking API 구현
- [x] **5.4** Trends API 구현
- [x] **5.5** Conversation CRUD API 구현
- [x] **5.6** `X-Session-Token` 세션 격리 구현
- [x] **5.7** CSV/JSON Export API 구현
- [x] **5.8** `/api/data/sync/github` API 문서화·권한 테스트
- [x] **5.9** technology·date range·metric 필터와 날짜 정렬 테스트
- [x] **5.10** `manual_demo` 데이터의 분석 API 제외 테스트
- [x] **5.11** Export 결과가 동일한 필터 범위와 일치하는지 테스트
- [x] **5.12** 입력 검증·권한·오류 응답 통합
- [x] **5.13** 대표 Acceptance Test 실행

### Phase 6 — Frontend 대시보드 및 상세 화면
- [x] **6.1** Vanilla HTML/CSS/JavaScript 기본 구조 구성
- [x] **6.2** 전체 기술 상위 5개 랭킹 대시보드 구현
- [x] **6.3** 랭킹 카드에 평균·Momentum·상태·근거 표시
- [x] **6.4** 기술 상세 화면 구현
- [x] **6.5** 최근 52주 주별 신규 Star 차트 구현
- [x] **6.6** Current Snapshot 표시를 주별 차트와 분리
- [x] **6.7** Summary·Compare·기간 선택 UI 구현
- [x] **6.8** 로딩·빈 데이터·오류 상태 구현
- [x] **6.9** Admin/Demo 데이터 관리 화면 구현

### Phase 7 — AI Chat 및 Conversation
- [x] **7.1** Chat 화면 구현
- [x] **7.2** Conversation 저장·목록·불러오기·삭제 연결
- [x] **7.3** 첫 방문 시 암호학적으로 안전한 256비트 `X-Session-Token` 생성
- [x] **7.4** Conversation 세션 토큰을 `localStorage`에 저장·전달
- [x] **7.5** `session_hash` 저장과 세션별 접근 제한 구현
- [x] **7.6** 토큰 삭제 후 기존 대화 재접근 불가 테스트
- [x] **7.7** 브라우저 간 대화 동기화를 v1 범위에서 제외
- [x] **7.8** 다른 세션의 대화 ID 접근 404 테스트
- [x] **7.9** AI 입력과 응답 API 연결
- [x] **7.10** 단일 기술 성장세 요약 질문 구현
- [x] **7.11** 두 기술 비교 질문 구현
- [x] **7.12** 계속 지켜볼 이유 설명 질문 구현
- [x] **7.13** 4개 Function Calling Tool Schema 구현
- [x] **7.14** Tool Dispatcher와 실제 Backend 계산 결과 재전달 구현
- [x] **7.15** 데이터 근거·기간·관측 주 수를 포함한 답변 검증
- [x] **7.16** Chat rate limit·입력 길이·모델 제한 구현

### Phase 8 — MCP 및 보너스 기능
- [x] **8.1** Trend Tool을 MCP 서버에 노출
- [x] **8.2** MCP Client에서 실제 Tool 호출 검증
- [x] **8.3** MCP 구현 불가 시 GPT Actions 대체안 검토 및 결정 기록
- [x] **8.4** CSV/JSON Export UI 연결
- [x] **8.5** Dark Mode 구현
- [x] **8.6** 테마 설정 유지 여부 확인
- [x] **8.7** Tool 호출 근거와 Workflow 문서화

### Phase 9 — 통합 테스트·배포·문서화
- [x] **9.1** 전체 Acceptance Test 통과
- [x] **9.2** 실제 데이터·가짜 데이터 혼입 여부 점검
- [x] **9.3** 공개 배포 보안 점검
- [x] **9.4** Backend Render 배포 및 `/docs` 확인
- [x] **9.5** Frontend Vercel 배포 및 Backend 통신 확인
- [x] **9.6** CORS·환경변수·관리자 키 운영 점검
- [x] **9.7** README 작성 및 신규 환경 실행 검증
- [x] **9.8** `Architecture.md`·`DATA_VALIDATION.md`·`DECISIONS.md` 보완
- [x] **9.9** `AI_USAGE_LOG.md` 작성
- [x] **9.10** 최종 데모 시나리오와 스크린샷 정리
- [x] **9.11** 남은 Open Questions를 결정하고 `DECISIONS.md`에 근거·대안·선택 결과 기록
- [x] **9.12** Firestore 어댑터·환경변수 활성화·저장 경계 테스트 구현
- [x] **9.13** 실제 Firebase 프로젝트 인증·Firestore 원격 smoke test 및 10개 저장소 적재
- [x] **9.14** GitHub Actions 주 1회 자동 동기화 워크플로 구성 및 운영 Secret 기준 문서화

---

## 1. 프로젝트 기준과 고정 결정

### 1.1 제품 목적
학습 시간과 업무 리소스를 투자할 가치가 있어 계속 지켜볼 AI 기술을 발견하도록 돕는다. 금융 투자 조언은 제공하지 않는다.

### 1.2 MVP 사용자
본인의 학습·업무를 위해 AI 기술 트렌드를 추적하는 개인.

### 1.3 초기 추적 기술 10개
| 기술 | GitHub 저장소 |
|---|---|
| LangGraph | `langchain-ai/langgraph` |
| LangChain | `langchain-ai/langchain` |
| LlamaIndex | `run-llama/llama_index` |
| CrewAI | `crewAIInc/crewAI` |
| PydanticAI | `pydantic/pydantic-ai` |
| DSPy | `stanfordnlp/dspy` |
| LiteLLM | `BerriAI/litellm` |
| vLLM | `vllm-project/vllm` |
| Ollama | `ollama/ollama` |
| Dify | `langgenius/dify` |

### 1.4 분석 규칙
- 주 지표: `weekly_new_stars`
- 누적 지표: `current_stargazer_count`로 분리
- 기본 기간: 최근 완결 주 13개
- Momentum 비교 기간: 직전 완결 주 13개
- 선택 기간: `4w`, `13w`, `26w`, `52w`
- `change_percent > 10`: `accelerating`
- `change_percent < -10`: `slowing`
- 그 외: `stable`
- 관측 주가 부족하면 `insufficient_data`
- API에 없는 주를 임의로 0으로 채우지 않음
- 진행 중인 주는 분석에서 제외

### 1.5 랭킹 규칙
전체 10개 기술을 대상으로 상위 5개를 반환한다. `weekly_new_stars_average` 내림차순을 1순위로 하고, 동률 또는 유사한 경우 `momentum_change_percent` 내림차순을 2순위로 한다.

---

## 2. 세션 운영 규칙

### 2.1 작업 시작 규칙
1. 이 문서의 전체 진행 현황을 확인한다.
2. 가장 먼저 남은 `[ ]` Task를 확인한다.
3. 관련 PRD·Architecture·검증 문서를 확인한다.
4. 작업 시작 전 해당 Task를 `[-]`로 변경한다.
5. 완료 시 산출물과 검증 결과를 기록하고 `[x]`로 변경한다.

### 2.2 Task 완료 기록 형식
```md
### YYYY-MM-DD — TASK-x.y
- 작업 내용:
- 변경 파일:
- 검증 명령/방법:
- 결과:
- 남은 이슈:
```

### 2.3 막힘 처리
- 외부 API 문제는 `DATA_VALIDATION.md`에 오류와 재현 방법을 기록한다.
- PRD와 구현이 충돌하면 임의로 결정하지 말고 `DECISIONS.md`에 대안과 영향을 기록한다.
- 보안·데이터 손실 위험은 `[!]`로 표시하고 해당 의존 작업을 진행하지 않는다.
- 환경 문제는 원인, 시도한 해결, 사용자 조치를 기록한다.

---

## 3. Phase별 상세 실행 기준

### Phase 0 — Data Spike 및 데이터 검증

#### 목표
10개 저장소 모두에서 주별 데이터를 확보할 수 있는지 검증한다. 이 Phase가 통과되지 않으면 수집·분석 구현을 확정하지 않는다.

#### 산출물
- `DATA_VALIDATION.md`
- 저장소별 원본 응답 요약
- 접근 가능 여부와 확보 가능한 완결 주 수
- `weekly_new_stars` 변환 규칙
- 실패 저장소와 대체 후보

#### 완료 조건
- 10개 저장소 각각의 결과가 기록됨
- 각 저장소의 104주 확보 여부가 `pass/fail`로 표시됨
- `week` 식별자와 주 경계 보존 규칙이 확정됨
- 실패 시 가짜 데이터를 만들지 않음

#### 다음 세션 첫 작업
Phase 0과 Phase 1의 1.1~1.4가 완료되었으므로 다음 세션은 `TASK-1.5`부터 시작한다.

### Phase 1 — Scaffold 및 아키텍처

#### 목표
Data Spike 결과를 반영해 개발자가 동일한 구조로 구현할 수 있는 프로젝트 뼈대와 아키텍처를 만든다.

#### 산출물
- `Architecture.md`
- `backend/`, `frontend/`
- 의존성 파일
- `.env.example`
- FastAPI `/docs`

#### 완료 조건
- Backend가 로컬에서 실행됨
- `/docs`에 기본 API가 노출됨
- 비밀 키가 소스 코드에 없음
- CORS와 오류 응답 정책이 있음

### Phase 2 — Firestore 데이터 모델 및 Admin 보호

#### 핵심 정책
- `technology_data` 필수 필드: `technology`, `repository`, `date`, `week_start_epoch`, `value`, `metric`, `source`, `source_type`, `analysis_eligible`, `collected_at`, `created_at`, `updated_at`
- 주별 데이터의 중복 기준: `repository + week_start_epoch + metric`
- 동일 중복 키가 들어오면 새 행을 만들지 않고 기존 행을 갱신하거나 무시하는 idempotent 정책을 적용한다.
- `technology_snapshots`에는 `technology`, `repository`, `current_stargazer_count`, `collected_at`을 저장한다.
- 수동 입력: `source=manual_demo`, `source_type=manual_entry`, `analysis_eligible=false`
- GitHub 수집: `source=github`, `source_type=github_star_history`, `analysis_eligible=true`
- `source`, `source_type`, `analysis_eligible`은 모두 서버가 결정하며 클라이언트 입력을 신뢰하지 않는다.
- GitHub 행은 일반 수정·삭제 API로 변경하지 않는다.
- 쓰기 요청은 `X-Admin-Key`로 보호한다.
- `ADMIN_API_KEY`는 프론트엔드 코드, HTML, localStorage, sessionStorage, 쿠키에 저장하지 않는다.
- 관리자가 실행 중 직접 입력한다.
- 키는 현재 세션 메모리에서만 사용한다.
- 새로고침·세션 종료 후 복원하지 않는다.
- 키가 없거나 불일치하면 쓰기·동기화 작업을 수행하지 않는다.

#### 완료 조건
- 권한 없는 쓰기 요청이 401/403으로 거부됨
- `analysis_eligible=true`를 보내도 수동 입력으로 저장됨
- 클라이언트가 `source_type`을 위조해도 서버가 `manual_entry` 또는 `github_star_history`로 강제함
- GitHub 행의 일반 PUT/DELETE가 거부됨
- 수동 Demo 행 CRUD가 보호된 경로에서 동작함

#### Current Snapshot 기준
- 현재 누적 Star는 주별 관측치와 별도의 `technology_snapshots` collection에 저장한다.
- snapshot에는 기술명·저장소·`current_stargazer_count`·수집 시각을 저장한다.
- snapshot 조회는 상세 화면의 현재 수치에만 사용한다.
- 주별 차트·Summary·Momentum·랭킹 계산에는 snapshot을 사용하지 않는다.

#### 데이터 모델 완료 조건
- 필수 필드 누락 요청이 4xx로 거부됨
- 숫자 필드와 날짜·주 식별자 형식이 검증됨
- 동일한 `repository + week_start_epoch + metric`이 중복 생성되지 않음
- `created_at`과 `updated_at`이 서버에서 관리됨

### Phase 3 — GitHub 수집 및 데이터 적재

#### 목표
검증된 10개 저장소의 데이터를 중복 없이 적재하고 주 1회 갱신한다. 주 1회 자동 갱신은 v1 필수 기능이며, 보호된 관리자 수동 동기화를 함께 제공한다.

#### 구현 주의사항
- API가 제공한 주별 버킷을 그대로 사용한다.
- API에 없는 주를 0으로 채우지 않는다.
- 진행 중인 주를 제외한다.
- 같은 저장소·같은 `week`는 중복 저장하지 않는다.
- 자동 갱신 실패 시 기존 정상 데이터를 삭제하지 않는다.

#### 완료 조건
- 10개 저장소 적재 결과가 확인됨
- 10개 × 104주 목표의 충족 여부가 측정됨
- 재실행해도 중복이 생기지 않음
- 수동 동기화 API가 관리자 보호 아래 동작함
- 현재 누적 Star가 `technology_snapshots`에 저장되고 마지막 수집 시각이 기록됨

### Phase 4 — Analytics 및 관심 기술 랭킹

```text
average(weekly_new_stars)

momentum_change_percent
= (recent_avg - previous_avg) / previous_avg * 100
```

`previous_avg == 0`이면 `change_percent=null`, `status=insufficient_baseline`으로 반환한다.

#### 완료 조건
- 동일 입력에 동일 결과가 나옴
- 4/13/26/52주 기간이 재현 가능함
- 경계값 ±10%가 `stable`로 처리됨
- 데이터 부족 기술이 순위에 부당하게 포함되지 않음
- 상위 5개 정렬 순서가 PRD와 일치함
- snapshot 값이 주별 차트·Momentum 계산에 사용되지 않음

### Phase 5 — Backend API 및 검증

#### 필수 API 및 계획된 보너스 API
```text
POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary
GET    /api/data/compare
GET    /api/data/ranking
GET    /api/data/trends
POST   /api/data/sync/github
POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}
POST   /api/chat
```

계획된 보너스 API:
```text
GET    /api/export/csv
GET    /api/export/json
```

#### 완료 조건
- 정상·실패·권한 오류 응답이 문서화됨
- Swagger에서 핵심 API를 실행할 수 있음
- 대표 Acceptance Test가 통과함
- 실제 데이터와 수동 데모 데이터의 분석 분리가 확인됨
- 수동 동기화 API가 관리자 키 없이 실행되지 않음
- Export 결과가 현재 필터 범위와 일치함
- `technology`, `date range`, `metric` 필터와 날짜 정렬 조합이 검증됨
- `manual_demo` 데이터가 Summary·Compare·Trends·Ranking에 포함되지 않음

### Phase 6 — Frontend 대시보드 및 상세 화면

#### 첫 화면
전체 10개 기술 중 상위 5개를 표시한다.

각 항목에는 순위·기술명, 주당 평균 신규 Star, Momentum, 상태, 한 줄 근거, 상세 이동을 표시한다.

#### 상세 화면
- 최근 13주 요약
- 직전 13주 비교
- 최근 52주 차트
- 저장소 정보
- AI 추가 질문 버튼

#### 완료 조건
- 실제 API 데이터로 렌더링됨
- 로딩·오류·데이터 부족 상태가 표시됨
- 누적 Star가 주별 신규 Star 차트에 잘못 사용되지 않음
- Current Snapshot은 별도 카드 또는 최신 시점 정보로만 표시됨
- 모바일·데스크톱에서 핵심 정보가 읽힘

### Phase 7 — AI Chat 및 Conversation

#### MVP 질문 범위
1. 단일 기술의 최근 성장세 요약
2. 두 기술의 주당 평균 신규 Star와 Momentum 비교
3. 학습 시간과 업무 리소스 관점에서 계속 지켜볼 이유 설명

#### Conversation 세션 격리 기준
- 첫 방문 시 브라우저가 암호학적으로 안전한 256비트 임의 `X-Session-Token`을 생성한다.
- 일반 Conversation 토큰은 `localStorage`에 저장한다. 이는 저장 금지 대상인 관리자 키와 별개다.
- 관리자 키는 어떠한 브라우저 저장소에도 저장하지 않는다.
- 브라우저는 `X-Session-Token`을 목록·조회·삭제·후속 채팅 요청에 전달한다.
- 서버는 원문 토큰을 저장하지 않고 해시한 `session_hash`만 저장한다.
- 다른 세션의 Conversation ID를 사용하면 404를 반환한다.
- 세션 토큰이 없거나 유효하지 않으면 현재 세션으로 간주하지 않는다.
- 토큰을 삭제하면 기존 대화에 재접근할 수 없다.
- 브라우저 간 대화 동기화는 v1 범위에 포함하지 않는다.

#### Function Calling Tool 목록
- `get_technology_summary`
- `compare_technologies`
- `get_trend_changes`
- `get_technology_history`

#### 답변 원칙
- LLM이 통계를 직접 계산하지 않는다.
- Backend Tool 결과만 수치 근거로 사용한다.
- 기간·관측 주 수·데이터 부족 여부를 표시한다.
- GitHub Star를 기술의 전체 성공으로 과장하지 않는다.

#### 완료 조건
- 질문 의도에 맞는 Tool이 실제 호출됨
- Tool 결과가 답변에 반영됨
- 대화가 저장·불러오기 됨
- 데이터가 없을 때 임의 수치를 만들지 않음
- 입력 길이·rate limit·모델 제한이 적용됨
- 다음 4개 Tool이 실제 Backend 계산 결과를 반환함: `get_technology_summary`, `compare_technologies`, `get_trend_changes`, `get_technology_history`
- LLM이 Tool 결과 없이 통계를 임의 계산하지 않음
- 다른 세션의 대화 목록·조회·삭제·후속 채팅이 차단됨

### Phase 8 — MCP 및 보너스 기능
- 연동 방식은 MCP Server로 확정한다.
- MCP 구현이 불가능한 경우 GPT Actions를 대체안으로 검토한다.
- MCP Client가 최소 하나의 Trend Tool을 실제 호출한다.
- CSV/JSON Export가 현재 필터 범위와 일치한다.
- Dark Mode가 동작한다.
- Tool 호출 과정과 근거를 문서화한다.

### Phase 9 — 통합 테스트·배포·문서화
- 전체 Acceptance Test를 통과한다.
- 실제 데이터·가짜 데이터 혼입 여부를 점검한다.
- 관리자 키가 배포된 프론트엔드에 노출되지 않는지 확인한다.
- Render Backend, Vercel Frontend, `/docs`, CORS를 검증한다.
- README만 보고 신규 환경에서 실행한다.
- PRD·Architecture·DATA_VALIDATION·DECISIONS의 용어를 대조한다.
- 최종 데모를 처음부터 끝까지 실행한다.
- PRD Open Questions는 모두 결정되어 `DECISIONS.md`에 기록되어 있다.
- 주 1회 자동 동기화는 v1 필수 기능으로 확정되어 있으므로 별도 선택 대상으로 취급하지 않는다.
- 각 결정에 근거·대안·선택 결과·트레이드오프를 `DECISIONS.md`에 기록한다.

---

## 4. 다음 세션 시작 안내

### 현재 시작 위치
Phase 0~9 구현과 운영 검증이 완료되었으며, GitHub Actions Repository secret 등록 후 주간 자동 동기화를 활성화한다.

### 다음 세션에서 할 일
1. GitHub Repository secret `RENDER_BACKEND_URL`을 등록한다.
2. GitHub Repository secret `ADMIN_API_KEY`를 Render 값과 동일하게 등록한다.
3. `workflow_dispatch`로 첫 자동 동기화를 실행한다.

### DATA_VALIDATION 표준 표
| 기술 | 저장소 | 접근 | 응답 구조 | 확보 주 수 | 104주 | 변환 가능 | 비고 |
|---|---|---:|---|---:|---:|---:|---|
| LangGraph | `langchain-ai/langgraph` | pending | pending | pending | pending | pending | |

### 세션 보고 형식
```md
## Session Report — YYYY-MM-DD

- 완료 Task:
- 변경 파일:
- 검증 결과:
- 발견한 문제:
- 결정이 필요한 사항:
- 다음 시작 Task:
```

---

## 5. 진행 로그

### Session 1 — 2026-10-06
- 완료 Task: `TASK-0.1`~`TASK-0.7`
- 변경 파일: `DATA_VALIDATION.md`, `DECISIONS.md`, `TASK.md`, `PRD.md`, `tools/validate_star_history.ps1`
- 검증 결과: 10개 저장소 모두 104주 이상, 7일 `days`, `weekly_new_stars` 변환 가능 확인
- 발견한 문제: Microsoft Agent Framework는 76주만 제공해 Dify로 교체; Windows PowerShell JSON 배열 축약 버그 수정
- 결정이 필요한 사항: 없음. 대체 결정과 스크립트 수정은 `DECISIONS.md`에 기록
- 다음 시작 Task: `TASK-1.1` — `Architecture.md` 작성 및 PRD 대조

### Session 2 — 2026-10-06
- 완료 Task: `TASK-1.1`~`TASK-1.5`
- 변경 파일: `Architecture.md`, `TASK.md`, `requirements.txt`, `.env.example`, `backend/__init__.py`, `backend/main.py`, `.venv/`
- 검증 결과: Architecture 필수 항목 12개 검색 검증 통과 (`ARCHITECTURE_REQUIREMENTS_OK`); Python 의존성 import 통과 (`IMPORTS_OK`); FastAPI `/health`와 `/openapi.json` 모두 HTTP 200, API 제목·버전·health 경로 확인; `.env.example` 필수 키 11개·실제 비밀 파일·프론트 비밀 참조 검증 통과; CORS preflight 200, 공통 400 오류 envelope 및 기본 로깅 확인
- 발견한 문제: 없음
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-2.2` — `technology_snapshots` 데이터 모델 구현

### Session 3 — 2026-10-06
- 완료 Task: `TASK-2.1`~`TASK-2.9`
- 변경 파일: `backend/models.py`, `backend/storage.py`, `backend/policies.py`, `backend/security.py`, `backend/api_data.py`, `backend/main.py`, `frontend/admin-key.ts`, `TASK.md`
- 검증 결과: `technology_data` 필수 필드·저장소 식별자·`weekly_new_stars`·GitHub source policy 검증 통과 (`DATA_MODEL_SHAPE_OK`, `EXPECTED_SOURCE_POLICY_REJECTION_EXIT=1`); snapshot의 현재 누적 Star·수집 시각·주별 지표 분리 검증 통과 (`SNAPSHOT_MODEL_OK`, warnings-as-errors); 동일 중복 키 upsert 시 1행 유지·기존 생성 시각 보존·값 갱신 확인 (`IDEMPOTENT_UPSERT_OK`); 클라이언트가 보낸 source metadata를 무시하고 trusted route에 따라 서버가 강제함을 확인 (`SERVER_SOURCE_POLICY_OK`); GitHub 일반 update/delete 거부 및 manual 행 CRUD 통과 (`GITHUB_UPDATE_EXIT=1`, `GITHUB_DELETE_EXIT=1`, `MANUAL_ROW_CRUD_OK`); 관리자 키 정답·오답·누락 검증 통과 (`ADMIN_KEY_POLICY_OK`); 프론트 관리자 키 메모리 전용 모듈의 저장소·쿠키·빌드 환경변수 참조 없음 확인 (`ADMIN_KEY_MEMORY_ONLY_OK`); Swagger OpenAPI에 `/api/data` GET/POST 및 `/api/data/{row_id}` PUT/DELETE가 노출되고 실제 CRUD·401 보호 검증 통과
- 발견한 문제: 첫 검증 명령의 PowerShell 한 줄 `try/except` 문법 오류; 검증 명령을 두 단계로 재실행해 모델 자체 문제 없음 확인
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-3.2` — API 응답을 주별 `weekly_new_stars`로 변환

### Session 4 — 2026-10-06
- 완료 Task: `TASK-3.1`~`TASK-3.9`
- 변경 파일: `backend/github_client.py`, `backend/ingestion.py`, `backend/snapshots.py`, `backend/refresh.py`, `backend/catalog.py`, `backend/sync.py`, `backend/api_data.py`, `backend/models.py`, `backend/policies.py`, `tools/validate_104_load.py`, `TASK.md`, `PRD.md`
- 검증 결과: fixture 기반 페이지 수집·`week/total/days` 정규화·`weekly_new_stars` 변환 통과 (`GITHUB_CLIENT_FIXTURE_OK`); GitHub 429 응답을 `GitHubAPIError`와 재시도 정보로 변환 확인 (`GITHUB_RATE_LIMIT_RAISED_EXIT=1`); 7일이 지나지 않은 주를 제외하는 필터 검증 통과 (`COMPLETE_WEEK_FILTER_OK`); 동일 fixture 재수집 시 2행 유지·2행 update·GitHub source policy 유지 확인 (`GITHUB_INGEST_IDEMPOTENCY_OK`); 현재 누적 Star를 `technology_snapshots`에 저장·조회하는 검증 통과 (`SNAPSHOT_COLLECT_STORE_OK`); 7일 주기·첫 실행·실패 시 마지막 성공 시각 보존 정책 통과 (`WEEKLY_REFRESH_POLICY_OK`); `/api/data/sync/github` OpenAPI 노출·무권한/오답 관리자 키 401 검증 통과; mock 기준 10개 저장소 sync 통과 (`SYNC_ALL_10_REPOSITORIES_OK`); 실제 GitHub API를 저장소별 최대 4페이지 호출해 10개 모두 119개 완결 주·104주 기준 통과 (`all_pass=true`)
- 발견한 문제: 저장소 정규식의 잘못된 이스케이프가 `stanfordnlp/dspy`를 거부하는 버그 발견·수정 후 10개 저장소 mock sync 재검증 통과 (`REPOSITORY_PATTERN_FIX_OK`, `SYNC_ALL_10_REPOSITORIES_OK`)
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-4.1` — 기간 규칙 `4w·13w·26w·52w` 구현

### Session 5 — 2026-10-06
- 완료 Task: `TASK-4.1`~`TASK-4.10`, `TASK-5.1`~`TASK-5.4`
- 변경 파일: `backend/analytics.py`, `backend/analytics_api.py`, `backend/api_data.py`, `tests/test_analytics.py`, `TASK.md`
- 검증 결과: 4·13·26·52주 기간 상수, 최근·직전 동일 기간, 합계·평균·최대·최소, Momentum 10% 경계, baseline 0, 관측치 부족, GitHub 행만 분석하는 규칙을 검증 통과 (`ANALYTICS_RULES_OK`); Summary·Compare·Ranking·Trends OpenAPI 등록 및 라우트 함수 검증 통과 (`ANALYTICS_API_OPENAPI_OK`, `ANALYTICS_API_FUNCTION_TEST_OK`); unittest 3개 통과
- 발견한 문제: 첫 fixture가 최근·직전 기간에 동일 주 키를 생성해 잘못된 테스트를 유발했으나, fixture 주차 offset을 수정해 재검증 통과. `TestClient`는 현재 Starlette/httpx2 호환 경고가 발생해 실제 라우트 함수와 OpenAPI로 검증함
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-5.5` — Conversation CRUD API 구현

### Session 6 — 2026-10-06
- 완료 Task: `TASK-5.5`~`TASK-5.13`
- 변경 파일: `backend/conversations.py`, `backend/conversation_api.py`, `backend/export_api.py`, `backend/api_data.py`, `backend/main.py`, `TASK.md`
- 검증 결과: 토큰 누락 401, Conversation 생성 201, 세션 A 목록만 1건, 세션 B 목록 0건, 교차 세션 조회·삭제 404, 본인 삭제 204, 서버 저장값이 원문 토큰이 아닌 SHA-256 hash임을 실제 서버에서 확인; Export JSON/CSV 필터 결과 일치; technology/date range/metric 필터와 날짜순 정렬 확인; manual_demo Summary 404로 분석 제외; sync API OpenAPI·401 권한 확인; 대표 Acceptance Test에서 필수 OpenAPI 경로 누락 없음, health/read/export 200, 보호 write/sync/session 401 확인 (`Acceptance=true`)
- 발견한 문제: 첫 교차 조회 검증 명령의 PowerShell curl 인자 조합 오류; URL 변수로 재실행해 404 확인
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-6.1` — Vanilla HTML/CSS/JavaScript 기본 구조 구성

### Session 7 — 2026-10-06
- 완료 Task: `TASK-6.1`~`TASK-6.9`
- 변경 파일: `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`, `frontend/admin-key.js`, `backend/main.py`, `backend/api_data.py`, `backend/snapshots.py`, `.env.example`, `TASK.md`
- 검증 결과: 정적 파일·랭킹 fetch·기간 선택·빈 데이터 상태·다크 모드·상세 API 연결·52주 bar chart·Current Snapshot 분리·Summary/Compare UI·Admin/Demo 입력·삭제 구조 검증 통과; Codex 브라우저에서 페이지 로드·비교 컨트롤·빈 데이터 안내·Admin Demo 폼 확인. `127.0.0.1:3000` CORS 누락을 수정한 뒤 재로드 검증 통과; Node JS syntax와 관리자 키 메모리 저장 정적 검증 통과 (`ADMIN_DEMO_FRONTEND_SYNTAX_OK`, `ADMIN_DEMO_MEMORY_STORAGE_OK`)
- 발견한 문제: 초기 브라우저 호출에서 localhost 전용 CORS로 API fetch가 실패했으나 `localhost:3000`과 `127.0.0.1:3000`을 모두 허용하도록 수정
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-7.1` — Chat 화면 구현

### Session 8 — 2026-10-06
- 완료 Task: `TASK-7.1`~`TASK-7.8`
- 변경 파일: `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`, `frontend/session-token.js`, `backend/conversations.py`, `backend/conversation_api.py`, `TASK.md`
- 검증 결과: Codex 브라우저에서 Chat UI·Conversation 목록·새 세션 버튼·질문 입력 확인; 32바이트 `crypto.getRandomValues` 기반 64자리 토큰 생성과 `localStorage` 저장 코드 정적 검증; Backend 세션 hash·목록·단건·삭제·교차 세션 404 검증 완료
- 발견한 문제: 없음
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-7.9` — AI 입력과 응답 API 연결

### Session 9 — 2026-10-06
- 완료 Task: `TASK-7.9`~`TASK-7.16`
- 변경 파일: `backend/ai_tools.py`, `backend/chat_api.py`, `backend/conversations.py`, `backend/main.py`, `frontend/app.js`, `TASK.md`
- 검증 결과: 4개 Tool schema·Dispatcher·Conversation 저장 통과 (`FUNCTION_TOOL_SCHEMAS_OK`, `CHAT_TOOL_DISPATCH_OK`); 자연어 단일 기술·성장세·두 기술 비교 라우팅 통과 (`NATURAL_CHAT_ROUTING_OK`); 실제 HTTP Chat에서 토큰 누락 401, Tool 응답·Conversation ID·답변 생성, 교차 세션 404, 2,001자 입력 422 확인; 브라우저에서 질문 입력 후 Conversation과 데이터 없음 근거 답변 확인
- 발견한 문제: 없음
- 결정이 필요한 사항: Chat rate limit 20회/시간, 입력 2,000자, Tool 계산은 Backend 결과만 사용하도록 결정. OpenAI 모델 선택은 Phase 9 `DECISIONS.md`에서 기록
- 다음 시작 Task: `TASK-8.1` — Trend Tool을 MCP 서버에 노출

### Session 10 — 2026-10-06
- 완료 Task: `TASK-8.1`~`TASK-8.3`
- 변경 파일: `backend/mcp_server.py`, `DECISIONS.md`, `TASK.md`
- 검증 결과: MCP `initialize`, `tools/list` 4개 Tool, `tools/call` 응답을 직접 호출 및 stdio 프로세스로 검증 통과 (`MCP_TOOLS_CALL_OK`); MCP 우선·GPT Actions 대체안 결정 기록 완료
- 발견한 문제: 없음
- 결정이 필요한 사항: 없음
- 다음 시작 Task: `TASK-8.4` — CSV/JSON Export UI 연결

### Session 11 — 2026-10-06
- 완료 Task: `TASK-8.4`~`TASK-8.7`
- 변경 파일: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`, `README.md`, `DECISIONS.md`, `.env.example`, `backend/chat_api.py`, `TASK.md`
- 검증 결과: Export JSON/CSV 버튼과 API 경로 연결, Dark Mode 및 localStorage 테마 유지, Tool 근거·Workflow README 기록, OpenAI Function Calling 선택 경로와 로컬 fallback 구현을 확인했다.
- 발견한 문제: 없음
- 결정이 필요한 사항: Chart는 Vanilla SVG/CSS, 모델은 `OPENAI_MODEL` 환경변수(기본 `gpt-4o-mini`), MCP는 경량 JSON-RPC 구현으로 확정
- 다음 시작 Task: `TASK-9.1` — 전체 Acceptance Test

### Session 12 — 2026-10-06
- 완료 Task: `TASK-9.1`~`TASK-9.3`, `TASK-9.6`~`TASK-9.11`
- 보류 Task: `TASK-9.4`~`TASK-9.5` — 실제 Render/Vercel 계정과 배포 URL 필요
- 변경 파일: `README.md`, `AI_USAGE_LOG.md`, `DEMO_SCENARIO.md`, `DEPLOYMENT_CHECKLIST.md`, `render.yaml`, `vercel.json`, `PRD.md`, `Architecture.md`, `DECISIONS.md`, `TASK.md`
- 검증 결과: unittest 3개, Backend compile, Frontend Node syntax, OpenAPI 필수 경로·health·CORS·보호 API·Chat·Export HTTP smoke test, 실제 데이터/수동 Demo 경계, MCP stdio, Codex 브라우저 Dashboard·Export·Chat·Dark Mode UI 로드 검증 통과
- 발견한 문제: 외부 배포는 계정·서비스 URL 없이는 실행할 수 없어 `[!]`로 보류. 로컬 구현과 배포 설정은 검증 완료
- 결정이 필요한 사항: 없음. Open Questions 5개를 모두 `DECISIONS.md`에 기록
- 다음 시작 Task: 실제 Render/Vercel URL 제공 시 `TASK-9.4`부터 외부 배포 smoke test 재개

### Session 13 — 2026-10-06
- 완료 Task: `TASK-9.12`
- 보류 Task: `TASK-9.13` — 실제 Firebase Service Account 자격증명 필요
- 변경 파일: `backend/firebase_client.py`, `backend/storage.py`, `backend/snapshots.py`, `backend/conversations.py`, `backend/api_data.py`, `backend/conversation_api.py`, `backend/main.py`, `.env.example`, `render.yaml`, `tests/test_firestore_adapters.py`, `TASK.md`
- 검증 결과: Firebase 환경변수가 없으면 기존 메모리 fallback, 완비되면 Firestore 어댑터를 선택하는 정책 확인; technology data upsert·GitHub 보호·snapshot 저장·Conversation 세션 격리 fake client 테스트 포함 전체 5개 테스트 통과
- 발견한 문제: 없음. 실제 Firebase 원격 연결은 사용자의 프로젝트 ID·Service Account 설정 후 실행해야 함
- 결정이 필요한 사항: 없음
- 다음 시작 Task: Firebase 자격증명 설정 후 `TASK-9.13` 원격 smoke test

### Session 14 — 2026-10-06
- 완료 Task: Firestore 어댑터 구현·검증 보완
- 변경 파일: `backend/firebase_client.py`, `backend/storage.py`, `backend/snapshots.py`, `backend/conversations.py`, `backend/api_data.py`, `backend/conversation_api.py`, `backend/main.py`, `tools/verify_firestore.py`, `tests/test_firestore_adapters.py`, `README.md`, `TASK.md`
- 검증 결과: 전체 unittest 5개 통과, Backend compile 통과, Firebase 미설정 상태의 안전한 fallback 및 비파괴 원격 smoke test 실행 경로 확인 (`FIRESTORE_IMPLEMENTATION_VERIFY_OK`)
- 발견한 문제: smoke test가 프로젝트 루트 외 실행 시 `backend`를 찾지 못하는 경로 문제가 있었으나 수정 후 재검증 통과
- 결정이 필요한 사항: 없음
- 다음 시작 Task: Firebase Service Account 환경변수 설정 후 `tools\verify_firestore.py` 실행

### Session 15 — 2026-10-06
- 완료 Task: `TASK-9.13`
- 변경 파일: C 드라이브 `.env` 설정 확인, `backend/api_data.py` rate limit 응답 보완
- 검증 결과: Firebase 원격 smoke test `FIRESTORE_REMOTE_SMOKE_OK`; GitHub 토큰 인증 확인; 10개 저장소 동기화 HTTP 200; Firestore `technology_data` 1,757행·`technology_snapshots` 10개·13주 Ranking 상위 5개 확인
- 발견한 문제: 최초 동기화는 Backend가 토큰 추가 전 실행되어 비인증 rate limit으로 실패했으나, 올바른 C 드라이브 Backend 재시작 후 성공
- 결정이 필요한 사항: 없음
- 다음 시작 Task: Render Backend·Vercel Frontend 실제 배포 및 외부 URL smoke test

### Session 16 — 2026-10-08
- 완료 Task: `TASK-9.4`, `TASK-9.5`, `TASK-9.14` 및 최종 운영 검증
- 변경 파일: `.github/workflows/weekly-github-sync.yml`, `README.md`, `TASK.md`, `backend/storage.py`, `frontend/index.html`, `frontend/styles.css`
- 검증 결과: Render health/OpenAPI/ranking/summary/compare/export API 200; Vercel에서 Top 5 카드·비교 선택지·Conversation 빈 상태 렌더링 확인; Firestore quota 회복 확인; GitHub Actions `cf98fa7` 기준 주간 동기화 성공(약 9분 49초)
- 운영 자동화: 매주 월요일 11:00 KST GitHub Actions가 보호된 `/api/data/sync/github`를 호출하며, `RENDER_BACKEND_URL`·`ADMIN_API_KEY` Repository secret을 사용한다.
- 발견한 문제: 없음
- 최종 상태: Phase 0~9 완료. 이후에는 정기 모니터링과 필요 시 데이터·비용 최적화만 수행한다.
