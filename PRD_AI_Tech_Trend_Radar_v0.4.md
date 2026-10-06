# PRD — AI 기술 트렌드 레이더
**문서 버전:** v0.4  
**프로젝트 유형:** AI Native Master Mission 2 — AI Agent 개발 / 나만의 AI 비서 구축  
**작업명:** AI 기술 트렌드 레이더  
**목적:** Codex 구현 기준 문서

## 0. v0.4 주요 변경사항

v0.2의 데이터 정의를 유지하면서, 구현과 검증에 필요한 다음 결정을 확정했다.

1. 모든 분석 기간을 완결된 GitHub 주 단위(`4w`, `13w`, `26w`, `52w`)로 통일
2. Momentum 임계값을 10%로 확정하고 비교·추세 규칙을 명확화
3. GitHub 수집값과 수동 CRUD 데모값을 분리하고 분석 대상 조건을 고정
4. 관리자 키는 공개 JavaScript에 포함하지 않고, 관리자가 실행 중 직접 입력하며 저장하지 않는 운영 방식으로 확정
5. 시나리오, Tool schema, 차트, 테스트 예시를 `weekly_new_stars`에 맞게 정렬
6. 실제 API 검증(Data Spike)을 Phase 0으로 확정
7. 최소 관측치 기준을 기간별 완결 주 N개 충족으로 확정


---

## 1. 제품 개요

AI 기술 학습자는 빠르게 등장하고 변화하는 AI/개발 기술의 흐름을 파악하기 어렵다. GitHub 등에서 누적 수치를 직접 확인할 수는 있지만, 최근 성장세·정체·변곡점·기술 간 상대적 변화까지 직접 비교하려면 별도의 데이터 수집과 분석이 필요하다.

**AI 기술 트렌드 레이더**는 AI/개발 기술의 시계열 데이터를 저장·분석하고, 사용자가 자연어로 질문하면 해당 데이터의 요약과 비교 결과를 근거로 설명하는 AI 분석 비서다.

이 서비스는 “무엇을 공부해야 한다”고 단정적으로 추천하는 서비스가 아니라, **기술 선택에 필요한 데이터 기반 판단 근거를 제공하는 분석 서비스**를 목표로 한다.

---

## 2. Target User

### 2.1 Primary User
- AI 기술을 학습 중인 학습자
- 새로운 AI/개발 프레임워크를 비교하고 싶은 학습자
- 기술의 현재 관심도와 성장 속도를 데이터로 확인하고 싶은 사용자

### 2.2 Secondary User
- 주니어 개발자
- 취업 준비생
- 새로운 기술 도입을 검토하는 개발자

---

## 3. Problem Statement

현재 사용자는 다음 문제를 가진다.

1. 여러 AI/개발 기술의 최근 변화 추이를 한 번에 비교하기 어렵다.
2. 누적 GitHub Star 같은 절대 수치만으로 최근 성장세를 판단하기 어렵다.
3. 기술별 변화의 의미를 직접 계산하고 해석해야 한다.
4. 최근 갑자기 성장하거나 둔화된 기술을 능동적으로 발견하기 어렵다.
5. 기술 트렌드를 확인하기 위해 여러 사이트와 수치를 직접 찾아봐야 한다.

---

## 4. Value Proposition

> AI 기술의 시계열 데이터를 수집·저장·분석하고, 사용자가 자연어로 질문하면 기술별 성장 흐름과 비교 결과를 데이터 근거와 함께 설명한다.

핵심 가치는 다음 3가지다.

1. **단일 기술 분석**
   - 특정 기술의 일정 기간 흐름을 분석한다.

2. **기술 간 비교**
   - 동일 기간·동일 기준으로 두 개 이상의 기술을 비교한다.

3. **변화 탐지**
   - 최근 성장·둔화·정체 등 변화가 큰 기술을 자동으로 식별한다.

---

## 5. 제품 원칙

### 5.1 분석 중심
AI는 “무조건 이 기술을 공부하라”고 단정하지 않는다.

### 5.2 근거 중심
AI의 주요 해석에는 가능한 한 다음을 포함한다.
- 분석 기간
- 사용 데이터
- 변화율 또는 비교 수치
- 해석
- 한계

### 5.3 계산과 해석 분리
- 평균, 최대/최소, 변화율, 기간 비교 등은 Python 코드가 계산한다.
- LLM은 사용자 의도 파악, 결과 설명, 비교 해석을 담당한다.

### 5.4 지표의 의미를 과장하지 않음
GitHub 기반 데이터는 “기술 인기 전체”가 아니라 **개발자 관심 및 repository activity의 한 지표**로 표현한다.

---

## 6. 핵심 User Scenarios

### Scenario A — 기술 비교

사용자는 LangChain과 LangGraph 중 최근 어떤 기술의 관심 증가 속도가 더 빠른지 알고 싶다.

**예시 질문**
> 최근 6개월 동안 LangChain과 LangGraph 중 관심도 증가가 더 빠른 기술은?

**기대 흐름**
1. 사용자 질문 입력
2. AI가 비교 의도 파악
3. 두 기술의 요약/시계열 데이터 조회
4. 동일한 완결 주간 기간의 주당 평균 신규 Star 비교
5. AI가 근거와 한계를 포함해 설명
6. 프론트에서 비교 그래프 표시 가능

---

### Scenario B — 최근 변화 탐지

사용자는 특정 기술을 지정하지 않고 최근 큰 변화가 있는 기술을 찾고 싶다.

**예시 질문**
> 최근 3개월 동안 갑자기 성장하기 시작한 기술이 있어?

**기대 흐름**
1. 추적 기술 목록 조회
2. 기술별 최근 기간의 주당 평균 신규 Star 계산
3. 직전 동일 길이 기간과 비교
4. 변화 폭이 큰 기술 추출
5. AI가 주요 후보와 근거 설명

---

### Scenario C — 단일 기술 심층 분석

사용자는 FastAPI의 최근 흐름을 알고 싶다.

**예시 질문**
> FastAPI의 최근 1년 흐름을 설명해줘.

**기대 흐름**
1. FastAPI 데이터 조회
2. 전체 기간 Summary 생성
3. 최근 4주/13주 변화 계산
4. 최고 성장 구간·둔화 구간 식별
5. AI가 전체 흐름/최근 흐름/특이 구간/한계 설명

---

## 7. User Stories

### US-01 단일 기술 분석
AI 기술 학습자로서 관심 기술의 최근 데이터와 변화 추세를 확인하고 싶다.  
그래야 해당 기술이 현재 어떤 흐름에 있는지 이해할 수 있다.

### US-02 기술 비교
AI 기술 학습자로서 두 개 이상의 기술을 같은 기간과 기준으로 비교하고 싶다.  
그래야 각 기술의 상대적인 성장 흐름을 데이터로 판단할 수 있다.

### US-03 변화 탐지
AI 기술 학습자로서 최근 추적 기술 중 변화가 큰 기술을 알고 싶다.  
그래야 내가 미처 주목하지 않았던 변화를 발견할 수 있다.

### US-04 자연어 질의
AI 기술 학습자로서 자연어로 기술 트렌드에 질문하고 싶다.  
그래야 통계값을 직접 계산하지 않아도 데이터의 의미를 이해할 수 있다.

### US-05 근거 확인
AI 기술 학습자로서 AI가 왜 그런 판단을 했는지 수치와 기간을 확인하고 싶다.  
그래야 AI 답변을 직접 검증할 수 있다.

### US-06 대화 기록
AI 기술 학습자로서 이전 분석 대화를 다시 불러오고 싶다.  
그래야 이전 분석을 기반으로 후속 질문을 할 수 있다.

---

## 8. 범위 정의

### 8.1 MUST — Mission 2 필수 구현

1. 최소 100개 이상의 시계열 데이터
2. FastAPI Backend
3. Firestore 연동
4. 데이터 CRUD
5. 데이터 Summary API
6. GPT 기반 AI Chat
7. Context Injection
8. Conversation 저장/목록/불러오기/삭제
9. HTML/CSS/JavaScript 프론트엔드
10. 로딩 UI
11. 데이터 요약 표시
12. Render Backend 배포
13. Vercel Frontend 배포
14. README 작성
15. 환경변수 및 API Key 안전 관리
16. CORS 설정
17. Swagger `/docs` 확인

### 8.2 MUST — 이번 프로젝트에서 구현할 보너스

1. OpenAI Function Calling
2. AI가 질문에 따라 내부 데이터 도구 선택
3. MCP Server 또는 GPT Actions 중 하나 연동  
   - 우선안: MCP Server
4. 추가 통계 지표 1개 이상
5. 기술 추세 그래프 1개 이상
6. CSV 또는 JSON Export
7. Dark Mode
8. Function Calling / MCP 호출 흐름 README 문서화

### 8.3 SHOULD

1. 여러 기술 동시 비교
2. 최근 4주/13주 주당 평균 신규 Star와 직전 동기간 대비 변화율
3. 직전 동일 기간 대비 성장 가속/둔화 계산
4. 기술별 최근 Momentum 지표
5. 분석 근거를 UI에서 별도 표시
6. 기술 필터/기간 선택 UI

### 8.4 COULD

1. GitHub Commit Activity 추가
2. Release Frequency 추가
3. 다중 지표 종합 분석
4. Google Trends 등 다른 데이터 소스 추가
5. 자동 데이터 갱신 스케줄러
6. 사용자별 관심 기술 Watchlist

### 8.5 OUT OF SCOPE — v1

1. 기술의 채용시장 수요를 확정적으로 판단
2. 실제 기업 도입률 추정
3. 기술 학습 우선순위 자동 확정
4. 다수 외부 데이터 소스의 완전 자동 통합
5. 인증/회원가입 시스템
6. 결제 기능
7. 모바일 네이티브 앱

---

## 9. 기술 스택

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- firebase-admin
- openai
- python-dotenv

### Database
- Firebase Firestore

### AI
- OpenAI API
- Function Calling / Tools

### Frontend
- HTML
- CSS
- Vanilla JavaScript
- 프레임워크 사용 금지

### Deployment
- Backend: Render
- Frontend: Vercel

### Bonus Integration
- MCP Server 우선 검토

---

## 10. 초기 데이터 전략

### 10.1 데이터 소스
초기 버전은 GitHub의 공개 repository 데이터와 Star History 데이터를 사용한다.

### 10.2 초기 추적 기술 후보
초기 구현은 3개 저장소로 시작한다.

초기 후보:
- LangChain: `langchain-ai/langchain`
- LangGraph: `langchain-ai/langgraph`
- FastAPI: `fastapi/fastapi`

기술명과 저장소 식별자는 분리해서 관리한다. 각 기술의 분석 단위는 MVP에서 하나의 GitHub 저장소다. 저장소가 접근 불가능하거나 104주를 제공하지 않으면 Data Spike 결과를 기록하고, 동일 기준을 만족하는 다른 저장소로 교체한다.

예:
```text
technology = LangGraph
repository = langchain-ai/langgraph
```

### 10.3 최소 데이터 확보 기준
미션의 최소 100개 데이터 포인트를 안정적으로 초과하고, 최근 기간과 직전 동일 기간을 비교할 수 있도록 다음을 기본 수집 기준으로 한다.

```text
3 repositories × 104 complete weeks = 312 weekly observations
```

각 저장소에서 최소 104개의 완결된 주별 관측치를 확보하는 것이 목표다. GitHub가 반환한 0건 주는 실제 관측치로 인정하며, API에 없는 주를 임의로 0으로 채우지 않는다. 100개 이상 충족 여부는 중복 제거 후 `source=github`, `analysis_eligible=true`인 실제 주별 행만 센다.

### 10.4 Primary Time-Series Metric

핵심 시계열 지표는 다음으로 고정한다.

```text
weekly_new_stars
```

정의:
- GitHub Star History에서 해당 주에 새로 발생한 Star 수
- 각 관측치는 1주 단위
- 기술 간 비교 시 같은 기간, 같은 metric을 사용
- 분석에는 진행 중인 주를 포함하지 않는다.

### 10.4.1 기간 및 주 경계

- API 응답의 `week`(Unix timestamp)를 원본 주 식별자로 보존한다. 표시용 `date`는 그 값에 대응하는 주 시작일이다.
- GitHub 문서상 주·일 경계가 반드시 UTC와 일치하지 않는다. 임의의 UTC 일별 집계로 재구성하지 않고 API가 제공한 주 버킷을 그대로 사용한다.
- 기본 기간은 `4w`, `13w`, `26w`, `52w`다. 예: `13w`는 최근 완결 주 13개를 뜻한다.
- Momentum의 이전 기간은 최근 기간 바로 앞의 동일한 완결 주 N개다.
- 30일·90일·6개월·1년이라는 사용자 표현은 각각 4·13·26·52주로 해석하고, 화면과 답변에는 실제 사용한 주 시작·종료일 및 주 수를 명시한다.

### 10.5 Current Snapshot Metric

현재 누적 Star 수는 주별 history와 분리해서 다룬다.

```text
current_stargazer_count
```

주의:
- `weekly_new_stars`는 주별 신규 Star 수
- `current_stargazer_count`는 현재 시점 누적 Star 수
- 둘을 동일한 의미로 취급하지 않는다.
- 과거 신규 Star 합계로 과거 시점의 실제 누적 Star 수를 단정하지 않는다.

### 10.6 MVP에서 제외하는 지표

```text
historical_cumulative_stars
```

과거 누적 Star 시계열은 MVP에서 직접 사용하지 않는다.

이유:
- Star는 이후 취소될 수 있다.
- 주별 신규 Star 합계와 실제 과거 누적 Star가 항상 일치한다고 단정하기 어렵다.
- 이번 프로젝트의 핵심은 누적 규모보다 최근 관심 변화와 성장 속도 분석이다.

### 10.7 데이터 해석 원칙

GitHub Star 기반 지표를 다음과 같이 표현한다.

**허용 표현**
- GitHub 관심 지표
- repository 관심도 변화
- 주별 신규 Star
- GitHub star 증가 속도

**금지 표현**
- 산업 점유율
- 실제 사용자 수
- 채용 수요
- 기술 전체 인기의 확정적 수치

## 11. 데이터 모델

Mission 2의 기본 `(date, value, memo)` 구조를 충족하되, 데이터 의미가 모호하지 않도록 필드를 명시적으로 확장한다.

### 11.1 `data` Collection

```json
{
  "id": "auto-generated",
  "technology": "LangGraph",
  "repository": "langchain-ai/langgraph",
  "date": "2026-01-04",
  "week_start_epoch": 1767484800,
  "value": 181,
  "metric": "weekly_new_stars",
  "memo": "GitHub Star History weekly total",
  "source": "github",
  "source_type": "github_star_history",
  "analysis_eligible": true,
  "api_version": "2026-03-10",
  "collected_at": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 11.2 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|---|---|---:|---|
| id | string | Y | Firestore document ID |
| technology | string | Y | 사용자에게 표시할 기술명 |
| repository | string | Y | `owner/repo` 형식 저장소 식별자 |
| date | date/string | Y | 주간 관측 기준일 |
| week_start_epoch | integer | Y | GitHub 응답의 원본 `week`; 주 식별 기준 |
| value | number | Y | `weekly_new_stars` 값으로 고정 |
| metric | string | Y | 기본값 `weekly_new_stars` |
| memo | string | N | 비고 |
| source | string | Y | `github` 또는 `manual_demo` |
| source_type | string | Y | `github_star_history` 또는 `manual_entry` |
| analysis_eligible | boolean | Y | 공개 분석 포함 여부; GitHub 수집 행만 `true` |
| api_version | string | N | 사용 API 버전 |
| collected_at | timestamp | N | GitHub 행에는 필수인 외부 데이터 수집 시각; 수동 행은 생성 시각 사용 |
| created_at | timestamp | Y | Firestore 생성 시간 |
| updated_at | timestamp | Y | Firestore 수정 시간 |

### 11.3 `value` 규칙

`value`는 MVP에서 반드시 다음 의미로 고정한다.

```text
value = weekly_new_stars
```

다른 metric을 추가할 경우 동일 collection에서 의미를 혼합하지 말고 별도 설계 결정을 `DECISIONS.md`에 기록한다.

GitHub 수집 시 `repository + week_start_epoch + metric`을 유일 키로 사용하여 재실행해도 중복 행을 만들지 않는다. 기존 수집 행은 동기화로만 갱신하며, 수동 CRUD는 별도 데모 행에 적용한다.

### 11.4 Current Snapshot

현재 누적 Star 수는 history row와 분리한다.

권장 구조:

```json
{
  "technology": "LangGraph",
  "repository": "langchain-ai/langgraph",
  "current_stargazer_count": 50231,
  "collected_at": "timestamp"
}
```

별도 `technology_snapshots` collection 사용을 권장한다.

### 11.5 CRUD 운영 원칙

Mission 2 요구사항 검증을 위해 data CRUD를 구현한다.

다만 실제 서비스 운영 관점에서는 GitHub 자동 수집 데이터를 사용자가 임의 수정하는 것은 바람직하지 않으므로, 해당 기능은 다음 성격으로 본다.

```text
Admin / Demo Data Management
```

- 자동 수집 데이터와 수동 입력 데이터는 source metadata로 구분한다.
- 공개 사용자에게는 읽기 중심 UI를 제공한다.
- 쓰기/수정/삭제 기능은 보호된 Admin/Demo 기능으로 제공한다.
- 수동 입력 행은 `source=manual_demo`, `analysis_eligible=false`로 저장한다. 기본 목록에는 필터로 확인할 수 있지만 Summary·Compare·Trends·AI 답변·100개 데이터 충족 계산에는 포함하지 않는다.
- 관리자도 GitHub 수집 행을 일반 CRUD로 직접 수정·삭제하지 않는다. 정정은 원본 API 재동기화와 기록된 운영 절차로 처리한다.

## 12. Conversation 데이터 모델

### `conversations` Collection

```json
{
  "id": "auto-generated",
  "title": "LangChain vs LangGraph 최근 6개월 비교",
  "messages": [
    { "role": "user", "content": "최근 6개월 동안 어떤 기술의 주당 신규 Star가 더 많았어?", "created_at": "timestamp" },
    { "role": "assistant", "content": "...", "created_at": "timestamp" }
  ],
  "session_hash": "sha256-of-anonymous-browser-token",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

회원가입 없이 브라우저별 대화를 제공한다. 첫 방문 시 브라우저가 암호학적으로 안전한 256비트 임의 토큰을 만들고 `localStorage`에 보관한다. 대화 및 채팅 API 요청은 `X-Session-Token` 헤더에 이를 전달하며, 서버는 해시값만 저장하고 목록·단건·삭제·후속 채팅을 항상 해당 세션으로 제한한다. 다른 세션의 ID는 404로 응답한다. 토큰을 지우면 이전 대화에 다시 접근할 수 없으며, 브라우저 간 동기화는 v1 범위 밖이다. API Key나 사용자 개인정보를 대화에 저장하지 않는다.

---

## 13. Summary 응답 설계

### `GET /api/data/summary`

예시 Query:
```text
/api/data/summary?technology=LangGraph&period=13w
```

예시 Response:

```json
{
  "technology": "LangGraph",
  "repository": "langchain-ai/langgraph",
  "period": {
    "start_week": "2026-06-28",
    "end_week": "2026-09-20",
    "weeks": 13
  },
  "count": 13,
  "metrics": {
    "weekly_new_stars_total": 1820,
    "weekly_new_stars_average": 140.0,
    "weekly_new_stars_max": 221,
    "weekly_new_stars_min": 71
  },
  "momentum": {
    "recent_average": 140.0,
    "previous_average": 105.0,
    "change_percent": 33.33,
    "status": "accelerating"
  },
  "trend": {
    "direction": "increasing",
    "basis": "weekly_new_stars_momentum"
  }
}
```

숫자는 예시이며 실제 구현에서는 저장 데이터로 계산한다.

`trend.direction`은 주별 신규 Star 유입 속도의 방향이다. Momentum이 `accelerating`이면 `increasing`, `slowing`이면 `decreasing`, `stable`이면 `stable`, 기준값·데이터가 부족하면 `unknown`으로 매핑한다. 누적 Star 수의 증감 방향을 뜻하지 않는다.

### 13.1 성장 속도 정의

MVP에서 “더 빨리 성장한다”는 의미는 다음으로 고정한다.

```text
동일 기간의 주당 평균 신규 Star가 더 높다.
```

즉 비교 기준은:

```text
average(weekly_new_stars)
```

이다.

### 13.2 Momentum 정의

Momentum은 최근 기간과 직전 동일 길이 기간의 평균 신규 Star를 비교한다.

```text
momentum_change_percent
=
(recent_avg - previous_avg) / previous_avg * 100
```

판정 기준 (`threshold_pct`는 퍼센트포인트 단위의 설정값):

```text
momentum_change_percent > threshold_pct
→ accelerating

momentum_change_percent < -threshold_pct
→ slowing

otherwise
→ stable
```

MVP의 기본 `threshold_pct`는 10으로 정한다. 경계값 ±10은 `stable`이다. 설정값과 근거를 `DECISIONS.md` 및 README에 기록한다.

### 13.3 예외 규칙

#### previous_avg == 0

```text
change_percent = null
status = insufficient_baseline
```

#### 관측치 부족

요청한 최근 N주와 직전 N주 중 한 주라도 실제 GitHub 관측치가 없으면:

```text
status = insufficient_data
```

AI는 해당 상태에서 추세나 가속 여부를 단정하지 않는다.

기간별 요약 평균은 최근 N개의 완결된 주가 모두 있을 때만 계산한다. 일부만 있으면 `insufficient_data`와 관측된 주 수를 반환한다. 비교는 동일한 두 기술 모두 같은 N개 주를 충족할 때만 순위를 낸다.

## 14. 기능 요구사항

### FR-01 데이터 추가
`POST /api/data`

사용자는 새로운 기술 데이터를 추가할 수 있어야 한다.

**Acceptance Criteria**
- 필수 필드 누락 시 4xx
- 숫자 필드 검증
- 요청 본문의 `source`와 `analysis_eligible` 값은 무시한다. 서버가 수동 입력이면 항상 `source=manual_demo`, `analysis_eligible=false`를 강제한다.
- 클라이언트가 `source=github` 또는 `analysis_eligible=true`를 보내도 GitHub 수집 행으로 저장되지 않는다.
- GitHub 수집 데이터는 일반 추가·수정·삭제 API로 생성하거나 변경할 수 없고, 전용 동기화 경로에서만 저장·갱신한다.
- 성공 시 생성 데이터 반환
- Firestore에 실제 저장

---

### FR-02 데이터 목록 조회
`GET /api/data`

**지원 조건**
- technology 필터
- date range 필터
- metric 필터
- 날짜 정렬

---

### FR-03 데이터 수정
`PUT /api/data/{id}`

**Acceptance Criteria**
- 존재하지 않는 ID → 404
- 수정 후 updated_at 갱신
- 유효성 검증
- `source=github`인 행의 일반 수정은 거부한다.
- 수정 요청의 `source`와 `analysis_eligible`은 클라이언트 입력을 사용하지 않으며 서버의 정책값을 유지한다.

---

### FR-04 데이터 삭제
`DELETE /api/data/{id}`

**Acceptance Criteria**
- 존재하지 않는 ID → 404
- 성공 응답 반환
- Firestore에서 실제 삭제

---

### FR-05 데이터 Summary
`GET /api/data/summary`

기술·기간 기준 Summary를 반환한다.

**필수 계산**
- period
- count
- weekly_new_stars_total
- weekly_new_stars_average
- weekly_new_stars_max
- weekly_new_stars_min
- trend

**추가 계산**
- 최근 기간 평균
- 직전 동일 기간 평균
- momentum change percent
- momentum status

현재 누적 Star 수가 필요한 경우 history와 분리된 snapshot 데이터에서 조회한다.

---

### FR-06 기술 비교
`GET /api/data/compare`

예시:
```text
/api/data/compare?technologies=LangChain,LangGraph&period=26w
```

동일 기간·동일 Metric을 기준으로 비교한다.

MVP 기본 비교 기준:

```text
average(weekly_new_stars)
```

추가로 각 기술의 momentum을 함께 반환한다.

데이터가 부족하거나 baseline이 없는 경우 해당 상태를 명시하고 순위를 강제로 만들지 않는다.

---

### FR-07 변화 탐지
`GET /api/data/trends`

최근 기간 기준 변화가 큰 기술을 반환한다.

가능한 결과:
- fastest_growth
- accelerating
- slowing
- stable

변화 판정 규칙은 코드로 명확히 정의한다.

---

### FR-08 대화 저장
`POST /api/conversations`

---

### FR-09 대화 목록
`GET /api/conversations`

---

### FR-10 특정 대화 조회
`GET /api/conversations/{id}`

---

### FR-11 대화 삭제
`DELETE /api/conversations/{id}`

---

### FR-12 AI Chat
`POST /api/chat`

Request 예시:

```json
{
  "message": "최근 6개월 동안 LangChain과 LangGraph 중 어떤 기술의 성장 속도가 더 빨라?",
  "conversation_id": null
}
```

---

## 15. AI Chat 처리 흐름

```text
User Question
    ↓
Backend가 사용자 질문 + Tool Schema를 OpenAI에 전달
    ↓
Model이 필요한 Tool Call 요청
    ↓
Backend가 Tool Arguments 검증
    ↓
Backend가 Analytics / Firestore Service 실행
    ↓
Tool Result 생성
    ↓
Tool Result를 OpenAI에 다시 전달
    ↓
Model이 근거 기반 Final Answer 생성
    ↓
Conversation 저장
    ↓
Frontend Response
```

### 15.1 책임 분리

**Model**
- 사용자 의도 파악
- 필요한 Tool 선택
- 결과 해석
- 자연어 답변 생성

**Backend**
- Tool arguments 검증
- 데이터 조회
- 통계 계산
- 예외 처리
- Tool result 생성
- Conversation 저장

**Analytics Service**
- 평균
- 최대/최소
- 기간 비교
- Momentum
- Trend 판정

LLM에게 원시 숫자 계산을 맡기지 않는다.

## 16. System Prompt 원칙

System Prompt는 아래 역할을 포함한다.

```text
당신은 AI/개발 기술 트렌드 분석 비서입니다.

주어진 데이터와 도구 호출 결과를 근거로 답변하세요.

원칙:
1. 제공되지 않은 수치를 만들어내지 마세요.
2. 계산 결과와 해석을 구분하세요.
3. GitHub 기반 지표를 산업 전체 사용량이나 채용 수요로 일반화하지 마세요.
4. 비교 질문에서는 동일 기간과 동일 지표를 기준으로 비교하세요.
5. 가능한 경우 핵심 근거 수치를 함께 제시하세요.
6. 데이터가 부족하면 부족하다고 명시하세요.
7. 추천보다 분석을 우선하세요.
```

---

## 17. AI 응답 권장 형식

가능하면 다음 형식으로 답변한다.

```text
[결론]
핵심 분석 결과

[데이터 근거]
기간 / 변화율 / 주요 수치

[해석]
무엇을 의미하는지 설명

[한계]
이 데이터만으로 판단할 수 없는 것
```

UI에서 반드시 네 개의 섹션으로 강제할 필요는 없지만 응답 품질 기준으로 사용한다.

---

## 18. Function Calling 설계

AI가 질문에 따라 적절한 도구를 선택하도록 한다.

### Tool 1
`get_technology_summary`

```text
목적:
특정 기술의 지정 기간 Summary 조회
```

Arguments:
```json
{
  "technology": "LangGraph",
  "period": "13w"
}
```

---

### Tool 2
`compare_technologies`

```text
목적:
2개 이상의 기술을 동일 기간/Metric 기준으로 비교
```

Arguments:
```json
{
  "technologies": ["LangChain", "LangGraph"],
  "period": "26w",
  "metric": "weekly_new_stars"
}
```

---

### Tool 3
`get_trend_changes`

```text
목적:
최근 변화가 큰 기술 탐지
```

Arguments:
```json
{
  "period": "13w",
  "limit": 5
}
```

---

### Tool 4
`get_technology_history`

```text
목적:
특정 기술의 원시 시계열 조회
```

Arguments:
```json
{
  "technology": "FastAPI",
  "start_date": "2026-01-01",
  "end_date": "2026-09-30"
}
```

---

## 19. MCP 요구사항

Function Calling에서 사용하는 핵심 분석 기능을 MCP Server에서도 호출 가능하도록 한다.

### MCP Tool 후보
- `get_technology_summary`
- `compare_technologies`
- `get_trend_changes`

### 검증 조건
1. MCP Client에서 Tool 목록 확인 가능
2. 최소 1개 Tool 실제 호출 성공
3. FastAPI/Firestore 데이터 결과 반환
4. README에 호출 흐름 기록
5. 스크린샷 또는 로그로 검증 가능

---

## 20. Frontend 요구사항

프레임워크 없이 HTML/CSS/Vanilla JavaScript로 구현한다.

### 20.1 Dashboard
표시:
- 추적 기술
- 최근 변화가 큰 기술
- Summary Card
- Trend Chart

### 20.2 AI Chat
- 사용자 메시지
- AI 메시지
- Loading 표시
- Error 표시
- 대화 자동 스크롤

### 20.3 Data Management
- 데이터 추가 Form
- 데이터 목록
- 데이터 수정
- 데이터 삭제
- 수정과 삭제를 모두 UI에서 실제 검증 가능하게 구현
- 해당 기능은 보호된 Admin/Demo 기능으로 제공

### 20.4 Conversation History
- 대화 목록
- 특정 대화 불러오기
- 대화 삭제

### 20.5 Analysis
- 기술 선택
- 기간 선택
- Summary 표시
- Chart 표시
- 비교 기능

### 20.6 Export
- CSV 또는 JSON 선택
- 현재 필터 범위 기준 Export

### 20.7 Dark Mode
- Toggle
- 새로고침 후 설정 유지 여부는 localStorage 사용 권장

---

## 21. Chart 요구사항

최소 하나 이상의 시계열 그래프를 제공한다.

권장:
- X축: date
- Y축: `weekly_new_stars` (주별 신규 Star 수)
- 현재 누적 Star 수(`current_stargazer_count`)는 별도 snapshot 지표이며 과거 주별 시계열 축에 사용하지 않는다.
- 여러 기술 비교 가능
- 동일 기간 범위 유지

가능하면 Chart.js CDN 사용을 검토한다.

프론트엔드는 프레임워크를 사용하지 않는다.

---

## 22. 비기능 요구사항

### NFR-01 Validation
Pydantic으로 API 입력값 검증

### NFR-02 Error Handling
최소한 다음 오류 처리:
- 잘못된 입력
- 데이터 없음
- Firestore 오류
- OpenAI API 오류
- 외부 데이터 API 오류

### NFR-03 Security
소스코드에 다음 정보를 하드코딩하지 않는다.
- OpenAI API Key
- Firebase Service Account
- 기타 Token

### NFR-04 CORS
로컬 개발 환경과 Vercel 배포 도메인을 환경변수로 관리한다.

### NFR-05 API Documentation
FastAPI Swagger `/docs` 접근 가능

### NFR-06 Loading
AI 응답 중 Loading 상태 표시

### NFR-07 Reproducibility
README만 보고 로컬 실행 가능해야 한다.

---

## 23. 공개 배포 보안 및 비용 통제

외부 배포 시 인증 없는 쓰기 API와 OpenAI 호출을 그대로 공개하지 않는다.

### 23.1 Write API 보호

다음 요청은 Demo/Admin Key 등 최소한의 보호 장치를 적용한다.

```text
POST /api/data
PUT /api/data/{id}
DELETE /api/data/{id}
POST /api/data/sync/github
```

확정 운영 방식:
- 요청은 `X-Admin-Key` header로 전달한다.
- 서버는 환경변수 `ADMIN_API_KEY`와 일치하는지 검증한다.
- `ADMIN_API_KEY`는 공개 저장소, 프론트엔드 번들, HTML, 브라우저 localStorage/sessionStorage, 쿠키에 포함하지 않는다.
- 관리자는 보호된 Admin/Demo 화면에서 실행 중 직접 입력한다.
- 키는 메모리의 현재 세션에서만 사용하고 새로고침·세션 종료 후 복원하거나 저장하지 않는다.
- 키가 없거나 일치하지 않으면 401/403을 반환하고 쓰기·동기화 작업을 수행하지 않는다.
- 읽기 API는 공개 가능하다.


### 23.2 Chat 호출 제한

`POST /api/chat`에는 비용 통제를 적용한다.

최소 요구:
- 입력 메시지 최대 길이 제한
- OpenAI output token 제한
- 요청 rate limit
- 허용 모델 고정
- 오류/초과 시 명확한 응답

구체 수치는 배포 전 `DECISIONS.md`에서 확정한다.

### 23.3 CORS

허용 origin은 환경변수로 관리한다.

```text
ALLOWED_ORIGINS
```

개발 환경과 Vercel 배포 도메인을 명시적으로 허용한다.

### 23.4 주의

Mission 2 범위를 초과하는 전체 회원가입/인증 시스템은 v1 범위에서 제외한다.

---

## 24. 환경 변수

Backend:

```env
OPENAI_API_KEY=
FIREBASE_SERVICE_ACCOUNT_JSON=
ALLOWED_ORIGINS=
GITHUB_TOKEN=
OPENAI_MODEL=
ADMIN_API_KEY=
```

Frontend:

```text
API_BASE_URL
```

Vanilla JS 배포 특성상 API URL 주입 방법은 Vercel 배포 구조에 맞게 별도 결정한다.

`.env`, Firebase Key 파일 등은 Git에 커밋하지 않는다.

---

## 25. 권장 Backend 구조

```text
backend/
├─ main.py
├─ requirements.txt
├─ .env.example
├─ app/
│  ├─ routers/
│  │  ├─ data.py
│  │  ├─ conversations.py
│  │  ├─ chat.py
│  │  └─ export.py
│  ├─ services/
│  │  ├─ firestore_service.py
│  │  ├─ analytics_service.py
│  │  ├─ github_service.py
│  │  ├─ ai_service.py
│  │  └─ conversation_service.py
│  ├─ models/
│  │  ├─ data.py
│  │  ├─ conversation.py
│  │  └─ chat.py
│  ├─ tools/
│  │  └─ trend_tools.py
│  └─ core/
│     ├─ config.py
│     └─ firebase.py
└─ tests/
```

역할 분리 원칙:
- Router: HTTP 입력/출력
- Service: 비즈니스 로직
- Model: Pydantic Schema
- Tool: LLM Function Calling Tool
- Core: 환경설정/공통 연결

---

## 26. 권장 Frontend 구조

```text
frontend/
├─ index.html
├─ css/
│  └─ style.css
├─ js/
│  ├─ api.js
│  ├─ chat.js
│  ├─ dashboard.js
│  ├─ data.js
│  ├─ conversations.js
│  ├─ charts.js
│  └─ theme.js
└─ assets/
```

---

## 27. API 목록

필수:

```text
POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}

GET    /api/data/summary
GET    /api/data/compare
GET    /api/data/trends

POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

POST   /api/chat
```

Bonus:

```text
GET /api/export/csv
GET /api/export/json
```

Optional:

```text
POST /api/data/sync/github
```

---

## 28. Analytics 규칙

분석 계산은 가능한 한 결정적 코드로 구현한다.

### 28.1 Primary Metric

```text
weekly_new_stars
```

### 28.2 Growth Speed

동일 기간의 주당 평균 신규 Star로 비교한다.

```text
growth_speed = average(weekly_new_stars)
```

### 28.3 Momentum

최근 기간과 직전 동일 길이 기간을 비교한다.

```text
recent_avg = average(recent_period.weekly_new_stars)
previous_avg = average(previous_period.weekly_new_stars)
```

`previous_avg > 0`인 경우:

```text
momentum_change_percent
=
(recent_avg - previous_avg) / previous_avg * 100
```

### 28.4 Momentum Status

```text
accelerating
slowing
stable
insufficient_baseline
insufficient_data
```

Threshold 값은 상수로 관리하고 README 및 `DECISIONS.md`에 남긴다.

### 28.5 Data Sufficiency

최근 기간 또는 직전 기간의 관측치가 최소 기준에 미달하면:

```text
status = insufficient_data
```

예:
- 12주 비교를 요청했는데 한 기간에 12개 주별 관측치가 없음
- repository 생성 시점 때문에 과거 baseline이 존재하지 않음

### 28.6 Zero Baseline

```text
previous_avg == 0
```

이면 percentage change를 계산하지 않는다.

```text
change_percent = null
status = insufficient_baseline
```

### 28.7 Historical Cumulative Stars

MVP에서는 과거 누적 Star 시계열을 계산하거나 사용자에게 실제 과거 누적값처럼 표시하지 않는다.

### 중요
LLM이 직접 숫자를 계산하도록 맡기지 않는다.

## 29. 테스트 요구사항

### Backend

#### Data
- 데이터 생성 성공
- 잘못된 타입 거부
- 목록 조회
- 필터 조회
- 수정
- 삭제
- 없는 ID 처리

#### Summary
- 정상 데이터 Summary
- 데이터 1개
- 데이터 없음
- 기간 필터
- 동일 기술 여러 날짜

#### Compare
- 2개 기술 비교
- 기간 불일치 방지
- 일부 기술 데이터 없음

#### Chat
- 일반 분석 질문
- 비교 질문
- 변화 탐지 질문
- 존재하지 않는 기술 질문
- 데이터 없는 질문
- OpenAI 오류

#### Conversations
- 저장
- 목록
- 단건 조회
- 삭제

---

## 30. 대표 Acceptance Test

### AT-01
사용자가 LangGraph 데이터를 추가하면 Firestore에 저장되고 목록에 표시된다.

### AT-02
사용자가 `/api/data/summary?technology=LangGraph` 호출 시 기간·개수·기본 통계·trend가 반환된다.

### AT-03
사용자가 “LangChain과 LangGraph를 비교해줘”라고 질문하면 AI가 두 기술 데이터를 기반으로 답한다.

### AT-04
AI 답변은 존재하지 않는 데이터 수치를 만들어내지 않는다.

### AT-05
AI 질문 시 Function Calling이 실제 내부 Tool을 호출한다.

### AT-06
이전 Conversation을 선택하면 메시지가 다시 표시된다.

### AT-07
현재 기술 데이터를 CSV 또는 JSON으로 다운로드할 수 있다.

### AT-08
Dark Mode 전환이 동작한다.

### AT-09
MCP Client에서 최소 하나의 Trend Tool을 실제 호출할 수 있다.

### AT-10
Render의 `/docs`와 Vercel Frontend가 외부에서 접속 가능하다.

---

## 31. 성공 기준

Mission 성공 기준:

- [ ] 100개 이상의 실제 시계열 데이터
- [ ] CRUD 정상 동작
- [ ] Firestore 저장
- [ ] Summary API 정상 동작
- [ ] Context Injection 확인
- [ ] AI Chat 정상 동작
- [ ] Conversation 저장/불러오기
- [ ] Render 배포
- [ ] Vercel 배포
- [ ] Swagger 확인
- [ ] README

Bonus 성공 기준:

- [ ] Function Calling 실제 Tool 호출
- [ ] MCP 또는 GPT Actions 실제 호출
- [ ] 추가 지표
- [ ] Trend Chart
- [ ] CSV/JSON Export
- [ ] Dark Mode
- [ ] Tool 호출 근거 및 Workflow 문서화

제품 품질 기준:

- [ ] AI 답변에서 데이터 근거 확인 가능
- [ ] Fact와 Interpretation 구분
- [ ] 데이터 없는 경우 정직하게 응답
- [ ] GitHub 지표의 한계 표시
- [ ] 동일 기준으로 기술 비교

---

## 32. README 필수 내용

1. 서비스 소개
2. 해결하려는 문제
3. Target User
4. 주요 기능
5. 기술 스택
6. 시스템 아키텍처
7. 데이터 구조
8. AI Context Injection 설명
9. Function Calling 구조
10. MCP 호출 흐름
11. 환경 변수
12. 로컬 실행 방법
13. Backend / Frontend / Swagger URL
14. 데이터 출처 및 지표 한계
15. 테스트 방법
16. 제출 스크린샷

---

## 33. Codex 구현 원칙

Codex는 아래 원칙을 지킨다.

1. PRD의 MUST 기능을 우선 구현한다.
2. 한 번에 전체 기능을 만들지 말고 작은 단위로 구현한다.
3. 각 단계 완료 후 실행 가능한 상태를 유지한다.
4. Router / Service / Model 책임을 분리한다.
5. API Key를 코드에 하드코딩하지 않는다.
6. LLM에게 통계 계산을 맡기지 않는다.
7. 실제 데이터가 없는 경우 가짜 수치를 사용자에게 보여주지 않는다.
8. 외부 API 실패 시 명확한 오류를 반환한다.
9. 새로운 라이브러리를 추가할 경우 이유를 기록한다.
10. 구현 변경으로 PRD와 달라질 경우 변경 이유를 `DECISIONS.md`에 기록한다.
11. 각 기능에는 최소한의 테스트 또는 검증 방법을 남긴다.
12. Frontend는 React/Vue 등 프레임워크를 사용하지 않는다.

---

## 34. 구현 전 Data Spike (Phase 0)

Codex는 본 구현 전에 대상 저장소 3개에 대해 실제 GitHub Star History 호출을 검증한다.

검증 항목:
- API 접근 성공 여부
- 반환 가능한 과거 기간
- 주별 `total` 의미 확인
- `days` 구조 확인
- 저장소별 최소 104주 확보 가능 여부
- rate limit 및 인증 필요 여부
- 응답을 `weekly_new_stars`로 변환 가능한지 확인

결과는 `DATA_VALIDATION.md`에 기록한다.

검증이 실패하면 임의로 데이터를 만들어 진행하지 말고 데이터 전략을 재검토한다.

---

## 35. Codex 권장 구현 순서

### Phase 0 — Data Spike
- 대상 저장소 3개의 GitHub Star History 실제 응답 검증
- 주별 `weekly_new_stars` 변환 가능 여부와 최소 104주 확보 여부 확인
- 결과를 `DATA_VALIDATION.md`에 기록

### Phase 1 — Scaffold
- Backend / Frontend 폴더 구성
- venv / requirements
- FastAPI 실행
- CORS
- `/docs`

### Phase 2 — Firestore
- Firebase 연결
- Data Model
- CRUD
- Swagger 테스트

### Phase 3 — Analytics
- Summary
- Compare
- Trend Detection
- Unit Test

### Phase 4 — Seed / Data Sync
- GitHub 데이터 수집
- 100개+ 데이터 확보
- Firestore 저장
- 결과 검증

### Phase 5 — Conversations
- 저장
- 목록
- 불러오기
- 삭제

### Phase 6 — AI Chat
- OpenAI 연결
- Context Injection
- 데이터 기반 응답

### Phase 7 — Function Calling
- Tool Schema
- Tool Dispatcher
- 실제 Tool 호출 검증

### Phase 8 — Frontend
- Dashboard
- Chat
- Data Management
- Conversations
- Summary

### Phase 9 — Bonus UX
- Chart
- Export
- Dark Mode

### Phase 10 — MCP
- MCP Server
- Tool 노출
- 외부 Client 호출 검증

### Phase 11 — Deployment
- GitHub
- Render
- Vercel
- CORS / Environment 변수

### Phase 12 — Documentation
- README
- Architecture
- DECISIONS
- TEST
- AI_USAGE_LOG

---

## 36. Definition of Done

프로젝트는 다음 조건이 모두 만족될 때 완료로 판단한다.

1. 사용자가 배포된 웹페이지에 접속할 수 있다.
2. 최소 100개 이상의 실제 시계열 데이터가 존재한다.
3. 데이터 CRUD가 정상 동작한다.
4. Summary가 코드로 계산된다.
5. 사용자가 단일 기술 분석 질문을 할 수 있다.
6. 사용자가 기술 비교 질문을 할 수 있다.
7. 사용자가 최근 변화 기술을 질문할 수 있다.
8. AI가 저장 데이터 또는 Tool 호출 결과를 기반으로 응답한다.
9. AI 답변의 핵심 근거를 확인할 수 있다.
10. Conversation 저장·불러오기가 가능하다.
11. Chart가 정상 표시된다.
12. CSV 또는 JSON Export가 가능하다.
13. Dark Mode가 동작한다.
14. Function Calling이 실제로 동작한다.
15. MCP 또는 GPT Actions를 통한 실제 Tool 호출이 검증된다.
16. Backend가 Render에 배포되어 `/docs`가 열린다.
17. Frontend가 Vercel에 배포되어 Backend와 통신한다.
18. README만 보고 다른 사람이 프로젝트를 실행할 수 있다.

---

## 37. 구현 중 반드시 기록할 의사결정

`DECISIONS.md`에 최소 다음 항목을 누적한다.

```text
Decision
Why
Alternatives
Trade-off
Result
```

필수 기록 후보:
- GitHub 지표 선택 이유
- `weekly_new_stars`와 `current_stargazer_count`를 분리한 이유
- 일별 vs 주별 데이터 단위
- Trend 판정 기준
- OpenAI model 선택
- Function Calling 구조
- MCP 선택 이유
- Firestore Collection 설계
- Frontend Chart 라이브러리 선택
- Render / Vercel 환경변수 관리 방식

---

## 38. 구현 전 남은 Open Questions

아래 항목만 구현 직전에 확정한다. 이미 확정된 정책은 Open Question으로 취급하지 않는다.

1. 초기 추적 기술 3개 확정
2. GitHub Star History 실제 응답 기간/접근 가능 여부 검증
3. Chart library
4. OpenAI model
5. MCP Python SDK 또는 구현 방식
6. Chat rate limit 수치
7. 자동 동기화 기능을 v1에 넣을지 여부

Open Question은 Codex가 임의로 추정해서 확정하지 말고, 구현에 영향을 크게 주는 경우 사용자에게 확인한다.
