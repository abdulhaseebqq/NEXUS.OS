from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.admin import router as admin_router
from src.api.auth import router as auth_router
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIRECTORY = PROJECT_ROOT / "uploads"

UPLOADS_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(
    title=APP_NAME,
    version=VERSION,
)

app.state.limiter = limiter
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
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    return response


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    logger.warning(f"Application Error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(f"HTTP Error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            error_code="HTTP_ERROR",
        ),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(f"Validation Error: {exc.errors()}")

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
    logger.warning(f"Rate Limit Exceeded: {request.url.path}")

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
    logger.error(f"Unhandled Error: {str(exc)}")

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
    admin_router,
    prefix="/api/v1",
    tags=["Admin"],
)
