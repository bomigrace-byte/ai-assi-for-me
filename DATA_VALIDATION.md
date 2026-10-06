# Data Validation — Phase 0

> 기준: `PRD.md` Final 1.0 / `TASK.md` Phase 0  
> 검증일: 2026-10-06 (Asia/Seoul)  
> 목적: 초기 추적 기술 10개가 GitHub 공식 Star History API에서 104개 이상의 완결 주와 `weekly_new_stars` 변환 가능한 응답을 제공하는지 확인

## 1. 검증 대상 API

```text
GET https://api.github.com/repos/{owner}/{repo}/stargazers/history
```

사용한 요청 조건:

- `per_page=30`
- `page=1..N` 페이지를 최신 주부터 과거 방향으로 순회
- `Accept: application/vnd.github+json`
- `X-GitHub-Api-Version: 2026-03-10`
- 공개 저장소에 대한 비인증 요청

응답의 각 항목은 다음 구조로 확인했다.

```json
{
  "week": 1791072000,
  "total": 79,
  "days": [39, 40, 0, 0, 0, 0, 0]
}
```

- `week`: 원본 주 식별자이며 `week_start_epoch`로 보존
- `total`: 해당 주의 신규 Star 수 → `value` 및 `weekly_new_stars`
- `days`: 일요일부터 시작하는 7일 배열
- API가 반환한 주 버킷을 그대로 사용하며 임의 UTC 재집계나 없는 주의 0 채우기는 하지 않음

공식 문서: [GitHub REST — Get repository star history](https://docs.github.com/en/rest/activity/starring)

## 2. 저장소별 검증 결과

| 상태 | 기술 | 저장소 | 확인 주 수 | 104주 | `days` 길이 | 변환 가능 | 비고 |
|---|---|---|---:|---|---:|---|---|
| PASS | LangGraph | `langchain-ai/langgraph` | 166 | PASS | 7 | PASS | 6 pages |
| PASS | LangChain | `langchain-ai/langchain` | 208 | PASS | 7 | PASS | 7 pages |
| PASS | LlamaIndex | `run-llama/llama_index` | 206 | PASS | 7 | PASS | 7 pages |
| PASS | CrewAI | `crewAIInc/crewAI` | 155 | PASS | 7 | PASS | 6 pages |
| PASS | PydanticAI | `pydantic/pydantic-ai` | 121 | PASS | 7 | PASS | 5 pages |
| PASS | DSPy | `stanfordnlp/dspy` | 196 | PASS | 7 | PASS | 7 pages |
| PASS | LiteLLM | `BerriAI/litellm` | 168 | PASS | 7 | PASS | 6 pages |
| PASS | vLLM | `vllm-project/vllm` | 192 | PASS | 7 | PASS | 수정 스크립트로 재검증 |
| PASS | Ollama | `ollama/ollama` | 172 | PASS | 7 | PASS | 수정 스크립트로 재검증 |
| PASS | Dify | `langgenius/dify` | 183 | PASS | 7 | PASS | Microsoft Agent Framework 대체 후보 |

## 3. 변환 규칙 검증

검증된 응답은 다음처럼 변환한다.

```text
technology       = 고정 기술명
repository       = owner/repo
date             = week epoch에 대응하는 표시용 주 시작일
week_start_epoch = response.week
value            = response.total
metric           = weekly_new_stars
source           = github
source_type      = github_star_history
analysis_eligible = true
```

중복 키:

```text
repository + week_start_epoch + metric
```

`days` 배열은 원본 검증 및 필요 시 세부 표시용으로 보존할 수 있지만, MVP 주 지표는 API가 제공한 `total`이다.

## 4. 현재 판정

- 접근 성공: 10/10
- 104주 확보 확인: 10/10
- 응답 구조 확인: 10/10
- `weekly_new_stars` 변환 가능: 10/10
- 전체 10개 저장소의 Phase 0 판정: **PASS**

초기 목록의 Microsoft Agent Framework는 실제 검증에서 76주만 제공되어 104주 기준을 충족하지 못했다. 개인 학습·업무 목적의 AI 애플리케이션 트렌드에 더 적합하고 183주를 제공한 Dify(`langgenius/dify`)를 대체 후보로 선택했다. vLLM은 최초 조회에서 90주 확인 후 rate limit으로 중단됐지만, rate limit 해제 후 수정된 스크립트로 192주와 7일 `days` 구조를 확인했다. Ollama도 172주와 7일 `days` 구조를 확인했다. Dify는 대체 후보 조회에서 183주와 7일 `days` 구조를 확인했다.

## 5. 검증 후속 처리

1. 대체 후보 Dify를 초기 추적 목록에 반영 완료
2. 10개 결과를 모두 `PASS`로 갱신 완료
3. `TASK.md`의 Phase 0 체크박스 갱신 완료
4. 대체 결정과 PowerShell JSON 파싱 수정 사항을 `DECISIONS.md`에 기록 완료
5. 다음 작업은 `TASK-1.1` Architecture.md 작성이다.

## 6. 실행 메모

- 비인증 GitHub API의 시간당 요청 한도에 도달했지만 rate limit 해제 후 재검증했다.
- 실제 데이터를 임의로 생성하거나 누락 주를 0으로 채우지 않았다.
- Windows PowerShell 5.1의 JSON 배열 축약 문제를 수정한 뒤 LangGraph로 재검증했다.
- 현재 10개 목록 중 Dify를 포함한 10개 저장소가 104주 기준과 7일 `days` 구조를 충족한다.
