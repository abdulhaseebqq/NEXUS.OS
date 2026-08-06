from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.dependencies import require_admin, require_super_admin
from src.core.responses import success_response
from src.crud.activity import (
    create_activity_log,
    get_activity_logs_by_user,
    get_all_activity_logs,
)
from src.crud.user import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user_role,
    update_user_status,
)
from src.database.database import get_db
from src.database.models import User
from src.schemas.user import (
    UserRoleUpdate,
    UserStatusUpdate,
)

router = APIRouter()


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "profile_image": user.profile_image,
        "created_at": user.created_at,
    }


def serialize_activity_log(log) -> dict:
    return {
        "id": log.id,
        "user_email": log.user_email,
        "action": log.action,
        "description": log.description,
        "created_at": log.created_at,
    }


@router.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    inactive_users = total_users - active_users

    return success_response(
        message="Admin dashboard retrieved successfully",
        data={
            "current_user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "role": current_user.role,
            },
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
            },
        },
    )


@router.get("/admin/activity-logs")
def activity_logs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    logs = get_all_activity_logs(db)

    return success_response(
        message="Activity logs retrieved successfully",
        data=[serialize_activity_log(log) for log in logs],
    )


@router.get("/admin/activity-logs/{user_email}")
def user_activity_logs(
    user_email: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    logs = get_activity_logs_by_user(
        db,
        user_email,
    )

    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No activity logs found for this user",
        )

    return success_response(
        message="User activity logs retrieved successfully",
        data={
            "user_email": user_email,
            "logs": [serialize_activity_log(log) for log in logs],
        },
    )


@router.get("/admin/users")
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = get_all_users(db)

    return success_response(
        message="Users retrieved successfully",
        data=[serialize_user(user) for user in users],
    )


@router.get("/admin/users/{user_id}")
def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return success_response(
        message="User details retrieved successfully",
        data=serialize_user(user),
    )


@router.put("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    allowed_roles = {
        "user",
        "admin",
        "super_admin",
    }

    if role_data.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    old_role = user.role

    updated_user = update_user_role(
        db,
        user,
        role_data.role,
    )

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="ROLE_CHANGED",
        description=(
            f"Changed role of {updated_user.email} "
            f"from {old_role} to {updated_user.role}"
        ),
    )

    return success_response(
        message="User role updated successfully",
        data={
            "previous_role": old_role,
            "user": serialize_user(updated_user),
        },
    )


@router.put("/admin/users/{user_id}/status")
def change_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own account status",
        )

    previous_status = user.is_active

    updated_user = update_user_status(
        db,
        user,
        status_data.is_active,
    )

    new_status = "active" if updated_user.is_active else "inactive"

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="USER_STATUS_CHANGED",
        description=(
            f"Changed account status of " f"{updated_user.email} to {new_status}"
        ),
    )

    return success_response(
        message="User account status updated successfully",
        data={
            "previous_is_active": previous_status,
            "user": serialize_user(updated_user),
        },
    )


@router.delete("/admin/users/{user_id}")
def remove_user(
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    deleted_user = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
    }

    delete_user(
        db,
        user,
    )

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="USER_DELETED",
        description=(
            f"Deleted user account: "
            f"{deleted_user['email']} "
            f"(ID: {deleted_user['id']})"
        ),
    )

    return success_response(
        message="User deleted successfully",
        data={
            "deleted_user": deleted_user,
        },
    )
