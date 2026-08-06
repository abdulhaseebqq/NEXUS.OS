from sqlalchemy.orm import Session

from src.database.models import ActivityLog


def create_activity_log(
    db: Session,
    user_email: str,
    action: str,
    description: str,
) -> ActivityLog:
    activity_log = ActivityLog(
        user_email=user_email,
        action=action,
        description=description,
    )

    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)

    return activity_log


def get_all_activity_logs(
    db: Session,
):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).all()


def get_activity_logs_by_user(
    db: Session,
    user_email: str,
):
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_email == user_email)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )
