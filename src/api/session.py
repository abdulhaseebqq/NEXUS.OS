from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.core.dependencies import bearer_scheme, get_current_active_user
from src.core.responses import success_response
from src.core.security import decode_access_token
from src.crud.activity import create_activity_log
from src.crud.session import (
    close_all_active_sessions,
    close_session,
    get_active_sessions,
    get_session_by_id,
)
from src.crud.token import (
    is_token_revoked,
    revoke_token,
)
from src.crud.user import get_user_by_email
from src.database.database import get_db

router = APIRouter()


def serialize_session(user_session) -> dict:
    return {
        "id": user_session.id,
        "device_name": user_session.device_name,
        "ip_address": user_session.ip_address,
        "user_agent": user_session.user_agent,
        "is_active": user_session.is_active,
        "created_at": user_session.created_at,
        "last_activity": user_session.last_activity,
        "logged_out_at": user_session.logged_out_at,
    }


@router.get("/users/me/sessions")
def list_current_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_current_active_user(
        credentials,
        db,
    )

    active_sessions = get_active_sessions(
        db,
        current_user.email,
    )

    return success_response(
        message="Active sessions retrieved successfully",
        data=[serialize_session(user_session) for user_session in active_sessions],
    )


@router.delete("/users/me/sessions")
def close_all_current_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_current_active_user(
        credentials,
        db,
    )

    active_sessions = get_active_sessions(
        db,
        current_user.email,
    )

    if not active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active sessions found",
        )

    closed_sessions = close_all_active_sessions(
        db,
        current_user.email,
    )

    revoked_count = 0

    for user_session in closed_sessions:
        if not is_token_revoked(
            db,
            user_session.refresh_token,
        ):
            revoke_token(
                db,
                user_session.refresh_token,
            )
            revoked_count += 1

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="ALL_SESSIONS_CLOSED",
        description=(f"Closed {len(closed_sessions)} active sessions"),
    )

    return success_response(
        message="All sessions closed successfully",
        data={
            "closed_sessions": len(closed_sessions),
            "revoked_tokens": revoked_count,
        },
    )


@router.delete("/users/me/sessions/{session_id}")
def close_current_user_session(
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_current_active_user(
        credentials,
        db,
    )

    user_session = get_session_by_id(
        db,
        session_id,
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if user_session.user_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot manage another user's session",
        )

    if not user_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already inactive",
        )

    closed_session = close_session(
        db,
        user_session,
    )

    if not is_token_revoked(
        db,
        closed_session.refresh_token,
    ):
        revoke_token(
            db,
            closed_session.refresh_token,
        )

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="SESSION_CLOSED",
        description=(
            f"Closed session ID {closed_session.id} " f"on {closed_session.device_name}"
        ),
    )

    return success_response(
        message="Session closed successfully",
        data={
            "session_id": closed_session.id,
            "device_name": closed_session.device_name,
            "logged_out_at": closed_session.logged_out_at,
        },
    )
