# 외부 배포 체크리스트

코드와 배포 설정은 검증했지만 실제 Render/Vercel 배포는 계정·서비스 URL이 필요하다.

## Render Backend

1. 저장소를 연결하고 `render.yaml` Blueprint를 적용한다.
2. `ADMIN_API_KEY`, `GITHUB_TOKEN`, `OPENAI_API_KEY`, `CORS_ORIGINS`를 Render Secret으로 입력한다.
3. `/health`, `/docs`, `/openapi.json`이 HTTP 200인지 확인한다.
4. `POST /api/data/sync/github`가 관리자 키 없이 401인지 확인한다.

## Vercel Frontend

1. 프로젝트 Root를 `frontend`로 지정하거나 정적 파일을 배포한다.
2. `frontend/config.js`의 `API_BASE`를 실제 Render Backend URL로 변경한 뒤 배포한다.
3. 브라우저에서 랭킹·Compare·Chat·Export를 확인한다.
4. Backend `CORS_ORIGINS`에 Vercel origin만 추가한다.

실제 URL이 생긴 뒤 `DEMO_SCENARIO.md`를 동일하게 재실행하고 TASK 9.4·9.5를 `[x]`로 변경한다.
