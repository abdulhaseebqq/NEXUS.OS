from fastapi import APIRouter

from src.core.config import (
    APP_NAME,
    VERSION,
)
from src.core.responses import success_response

router = APIRouter()


@router.get("/")
def home():
    return success_response(
        message=f"Welcome to {APP_NAME}",
        data={
            "application": APP_NAME,
            "version": VERSION,
            "status": "Running",
        },
    )
