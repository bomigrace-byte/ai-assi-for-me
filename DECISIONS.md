# Implementation Decisions

> 2026-10-28 현재 운영 판정은 `DEPLOYMENT_CHECKLIST.md`를 따른다. 아래 과거 결정의 검증 결과는 당시의 기록이다.

## Decision 001 — Microsoft Agent Framework를 Dify로 교체

- 날짜: 2026-10-06
- 단계: Phase 0 Data Spike
- 결정: 초기 추적 10개 중 `microsoft/agent-framework`를 제외하고 `langgenius/dify`를 포함한다.

### Why

`microsoft/agent-framework`는 실제 GitHub Star History API에서 76개 주만 반환되어 PRD의 저장소별 최소 104개 완결 주 기준을 충족하지 못했다. Dify는 동일 검증에서 183개 주와 7일 `days` 구조를 제공했다. 또한 Dify는 개인의 학습·업무 리소스 투자 판단과 직접 관련된 AI 애플리케이션 플랫폼이다.

### Alternatives

- Open WebUI: 158개 주, 기준 충족
- AutoGPT: 187개 주, 기준 충족
- Microsoft Agent Framework 유지: 데이터 기준 미충족

### Trade-off

Dify를 선택하면 엔터프라이즈 에이전트 프레임워크 비교 비중은 줄어들지만, 초기 데이터의 동일 기간 비교 가능성과 개인 사용자 관점의 제품 적합성이 높아진다.

### Result

초기 추적 목록을 Dify로 확정하고 PRD·TASK·검증 스크립트·DATA_VALIDATION을 동기화했다.

## Decision 002 — Windows PowerShell JSON 배열 정규화

- 날짜: 2026-10-06
- 단계: Phase 0 Data Spike
- 결정: 검증 스크립트에서 Windows PowerShell 5.1의 배열 축약 응답을 주별 객체 배열로 정규화한다.

### Why

초기 스크립트는 30주 응답을 1개 객체로 세어 104주 검증을 잘못 실패시켰다. `week`·`total`·`days` 배열을 인덱스별 주별 객체로 재구성한 뒤 LangGraph 실데이터에서 166주와 7일 `days` 구조를 확인했다.

### Result

`tools/validate_star_history.ps1`에 응답 정규화 로직을 반영하고 실제 터미널 검증으로 통과시켰다.

## Decision 003 — MCP Server 연동 방식 선택

- 날짜: 2026-10-06
- 단계: Phase 8 MCP
- 결정: Trend Tool 연동은 MCP Server를 우선 구현하고, 구현 불가 시 GPT Actions를 대체안으로 검토한다.

### Why

MCP는 `get_technology_summary`, `compare_technologies`, `get_trend_changes`, `get_technology_history`를 동일한 Backend Dispatcher에 연결해 Chat과 외부 Client가 같은 계산 결과를 사용할 수 있다. 임의의 LLM 계산을 방지하고 Tool 결과의 재현성을 유지하기 쉽다.

### Trade-off

MCP 표준 처리와 Client 연결 검증이 추가로 필요하다. 대신 GPT Actions에 종속되지 않고 로컬·서버 환경에서 같은 Tool 계약을 재사용할 수 있다.

### Result

경량 JSON-RPC MCP Server를 구현하고 `tools/list` 및 `tools/call` 실제 호출을 터미널에서 검증했다.

## Decision 004 — Chat 운영 제한

- 날짜: 2026-10-06
- 단계: Phase 7 AI Chat
- 결정: 입력은 2,000자 이하, 세션별 시간당 20회로 제한하며 Backend Tool 결과만 답변 근거로 사용한다.

### Why

개인 MVP의 비용·오용·긴 입력에 따른 불안정성을 제한하고, 주당 평균 신규 Star·Momentum 계산을 LLM이 임의로 재계산하지 않도록 하기 위함이다.

## Decision 005 — UI·AI 구현 선택

- 날짜: 2026-10-06
- 단계: Phase 9 통합·문서화
- 결정: Chart는 외부 라이브러리 없이 Vanilla SVG/CSS bar chart로 구현하고, OpenAI 모델은 `OPENAI_MODEL` 환경변수로 지정하며 기본값은 `gpt-4o-mini`로 둔다. MCP는 별도 Python SDK 대신 프로젝트 내부의 경량 JSON-RPC 구현을 사용한다.

### Why

MVP의 차트는 52개 주별 값을 단순 비교하는 목적이므로 외부 Chart 라이브러리보다 번들·배포 복잡도가 낮은 SVG/CSS가 적합하다. 모델은 배포 환경별 교체 가능성이 있으므로 코드에 고정하지 않고 환경변수로 분리한다. MCP는 현재 Tool Schema와 Dispatcher를 재사용하는 범위가 작아 SDK 의존성을 추가하지 않는다.

### Alternatives

- Chart.js/Recharts: 기능은 풍부하지만 MVP 번들과 의존성이 증가한다.
- OpenAI 모델 하드코딩: 단순하지만 비용·가용성 변화에 대응하기 어렵다.
- MCP Python SDK: 표준 편의성은 있으나 현재 JSON-RPC 범위에는 과하다.

### Trade-off

SVG 차트는 복잡한 상호작용이 제한되고, 경량 MCP 구현은 표준 기능 범위가 좁다. 대신 현재 MVP 요구를 충족하면서 운영 선택지를 환경변수와 대체안으로 남긴다.

## Decision 006 — 공개 분석 결과 사전 계산과 조건 조회

- 날짜: 2026-10-28
- 결정: 기존 FastAPI·Render·Firestore 구조를 유지하고, 주간 동기화 완료 시 4·13·26·52주 요약·랭킹을 `analytics_snapshots/current` 한 문서에 저장한다. 문서가 없으면 첫 공개 분석 요청에서 원본을 한 번 읽어 생성한다. 기술 상세·현재 Star·대화 목록은 각각 기술 또는 세션 조건으로 조회한다.

### Why

기존 공개 분석 요청의 캐시 미스는 `technology_data` 전체를 읽었다. 사전 계산 문서는 평상시 분석 요청을 문서 1건 읽기로 제한하고, 조건 조회는 다른 기술·세션의 문서를 읽지 않게 한다. 수동 Demo 데이터는 계속 공식 분석에서 제외한다.

### Trade-off 및 현재 검증

최초 문서 생성과 주간 동기화는 원본 전체 읽기 및 기존 대량 upsert 비용을 남긴다. 여러 인스턴스의 최초 동시 요청은 중복 생성될 수 있다. 로컬 자동 테스트 19개는 통과했고 커밋 `6cbb676`의 배포도 확인했지만, Firestore 할당량 초과로 원격 분석 문서 생성과 실제 절감량은 아직 검증하지 못했다. 따라서 운영 절감률을 확정 수치로 주장하지 않는다.
