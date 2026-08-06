from typing import Any


def success_response(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    error_code: str,
    details: Any = None,
) -> dict:
    return {
        "success": False,
        "message": message,
        "error": {
            "code": error_code,
            "details": details,
        },
    }
