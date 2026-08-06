from fastapi import APIRouter

from src.core.responses import success_response

router = APIRouter()


@router.get("/health")
def health():
    return success_response(
        message="Health check completed successfully",
        data={
            "status": "OK",
        },
    )
