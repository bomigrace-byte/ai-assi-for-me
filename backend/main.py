import logging
import os
from json import JSONDecodeError, loads

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from .api_data import router as data_router
from .analytics_api import router as analytics_router
from .conversation_api import router as conversation_router
from .export_api import router as export_router
from .chat_api import router as chat_router


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("ai-tech-trend-radar")


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    try:
        parsed = loads(raw)
        if isinstance(parsed, list):
            return [str(origin) for origin in parsed]
    except JSONDecodeError:
        pass
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="AI Tech Trend Radar API",
    version="1.0.0",
    description="Backend API for weekly GitHub star trend analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key", "X-Session-Token"],
)

app.include_router(data_router)
app.include_router(analytics_router)
app.include_router(conversation_router)
app.include_router(export_router)
app.include_router(chat_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": f"HTTP_{exc.status_code}", "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "요청 형식이 올바르지 않습니다.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled application error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "서버 내부 오류가 발생했습니다."}},
    )


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    logger.info("health check")
    return {"status": "ok"}


@app.get("/debug/error", include_in_schema=False)
def debug_error() -> None:
    """Development-only endpoint used to verify the common error envelope."""
    raise HTTPException(status_code=400, detail="debug error")
