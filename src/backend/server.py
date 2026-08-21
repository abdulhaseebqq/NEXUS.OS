from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.api.admin import router as admin_router
from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.health import router as health_router
from src.api.home import router as home_router
from src.api.profile import router as profile_router
from src.api.session import router as session_router
from src.api.system import router as system_router
from src.core.config import APP_NAME, VERSION
from src.core.exceptions import AppException
from src.core.logger import logger
from src.core.rate_limit import limiter
from src.core.responses import error_response
from src.core.settings import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIRECTORY = PROJECT_ROOT / "uploads"

UPLOADS_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    debug=settings.DEBUG,
    description=(
        "NEXUS.OS backend API for authentication, user profiles, "
        "sessions, administration, system management, AI chat, "
        "and platform services."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "NEXUS.OS",
    },
    license_info={
        "name": "Proprietary",
    },
)

app.state.limiter = limiter

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)

app.add_middleware(SlowAPIMiddleware)

app.mount(
    "/uploads",
    StaticFiles(
        directory=UPLOADS_DIRECTORY,
    ),
    name="uploads",
)

logger.info("NEXUS OS Backend Started Successfully")


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    logger.info(
        "%s %s",
        request.method,
        request.url.path,
    )

    response = await call_next(request)

    return response


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next,
):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    logger.warning(
        "Application Error: %s",
        exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
        ),
    )


HTTP_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
}


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        "HTTP Error: %s",
        exc.detail,
    )

    error_code = HTTP_ERROR_CODES.get(
        exc.status_code,
        "HTTP_ERROR",
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            error_code=error_code,
        ),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Validation Error: %s",
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content=error_response(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details=exc.errors(),
        ),
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(
    request: Request,
    exc: RateLimitExceeded,
):
    logger.warning(
        "Rate Limit Exceeded: %s",
        request.url.path,
    )

    return JSONResponse(
        status_code=429,
        content=error_response(
            message=("Too many requests. " "Please try again later."),
            error_code="RATE_LIMIT_EXCEEDED",
        ),
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled Error: %s",
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal Server Error",
            error_code="INTERNAL_SERVER_ERROR",
        ),
    )


app.include_router(
    home_router,
    prefix="/api/v1",
    tags=["Home"],
)

app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["Health"],
)

app.include_router(
    system_router,
    prefix="/api/v1",
    tags=["System"],
)

app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["Authentication"],
)

app.include_router(
    profile_router,
    prefix="/api/v1",
    tags=["Profile"],
)

app.include_router(
    session_router,
    prefix="/api/v1",
    tags=["Sessions"],
)

app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["Chat"],
)

app.include_router(
    admin_router,
    prefix="/api/v1",
    tags=["Admin"],
)
