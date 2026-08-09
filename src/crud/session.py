from sqlalchemy.orm import Session

from src.core.datetime_utils import utc_now
from src.database.models import UserSession


def create_session(
    db: Session,
    user_email: str,
    refresh_token: str,
    device_name: str,
    ip_address: str,
    user_agent: str,
):
    session = UserSession(
        user_email=user_email,
        refresh_token=refresh_token,
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_active_sessions(
    db: Session,
    user_email: str,
):
    return (
        db.query(UserSession)
        .filter(
            UserSession.user_email == user_email,
            UserSession.is_active.is_(True),
        )
        .order_by(UserSession.created_at.desc())
        .all()
    )


def get_session_by_id(
    db: Session,
    session_id: int,
):
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_session_by_refresh_token(
    db: Session,
    refresh_token: str,
):
    return (
        db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
    )


def update_session_activity(
    db: Session,
    session: UserSession,
):
    session.last_activity = utc_now()

    db.commit()
    db.refresh(session)

    return session


def close_session(
    db: Session,
    session: UserSession,
):
    session.is_active = False
    session.logged_out_at = utc_now()

    db.commit()
    db.refresh(session)

    return session


def close_all_active_sessions(
    db: Session,
    user_email: str,
):
    sessions = get_active_sessions(
        db,
        user_email,
    )

    closed_at = utc_now()

    for session in sessions:
        session.is_active = False
        session.logged_out_at = closed_at

    db.commit()

    return sessions
