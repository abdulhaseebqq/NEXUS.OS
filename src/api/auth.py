from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.core.datetime_utils import utc_now
from src.core.rate_limit import limiter
from src.core.responses import success_response
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from src.crud.activity import create_activity_log
from src.crud.session import (
    close_session,
    create_session,
    get_session_by_refresh_token,
    update_session_activity,
)
from src.crud.token import is_token_revoked, revoke_token
from src.crud.user import (
    authenticate_user,
    create_new_verification_token,
    create_password_reset_token,
    create_user,
    get_user_by_email,
    get_user_by_password_reset_token,
    get_user_by_verification_token,
    reset_user_password,
    verify_user_email,
)
from src.database.database import get_db
from src.schemas.reset_password import ForgotPasswordRequest, ResetPasswordRequest
from src.schemas.user import LogoutRequest, RefreshTokenRequest, UserCreate, UserLogin
from src.schemas.verification import EmailVerificationRequest, ResendVerificationRequest

router = APIRouter()


def get_client_ip(request: Request) -> str:
    if request.client is None:
        return "Unknown"

    return request.client.host


def get_user_agent(request: Request) -> str:
    return request.headers.get(
        "user-agent",
        "Unknown",
    )


def get_device_name(user_agent: str) -> str:
    user_agent_lower = user_agent.lower()

    if "android" in user_agent_lower:
        return "Android Device"

    if "iphone" in user_agent_lower:
        return "iPhone"

    if "ipad" in user_agent_lower:
        return "iPad"

    if "windows" in user_agent_lower:
        return "Windows Device"

    if "macintosh" in user_agent_lower:
        return "Mac Device"

    if "linux" in user_agent_lower:
        return "Linux Device"

    return "Unknown Device"


@router.post(
    "/users/signup",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
def signup(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    created_user = create_user(
        db,
        user,
    )

    create_activity_log(
        db=db,
        user_email=created_user.email,
        action="SIGNUP",
        description=("User account created. " "Email verification is required."),
    )

    return success_response(
        message=("User account created successfully. " "Please verify your email."),
        data={
            "id": created_user.id,
            "full_name": created_user.full_name,
            "email": created_user.email,
            "role": created_user.role,
            "is_active": created_user.is_active,
            "is_email_verified": (created_user.is_email_verified),
            "profile_image": created_user.profile_image,
            "verification": {
                "token": (created_user.email_verification_token),
                "expires_at": (created_user.email_verification_expires_at),
            },
        },
    )


@router.post("/users/verify-email")
@limiter.limit("10/minute")
def verify_email(
    request: Request,
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_verification_token(
        db,
        verification_data.token,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    expires_at = user.email_verification_expires_at

    if expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has no expiry",
        )

    if expires_at < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )

    verified_user = verify_user_email(
        db,
        user,
    )

    create_activity_log(
        db=db,
        user_email=verified_user.email,
        action="EMAIL_VERIFIED",
        description="User email verified successfully",
    )

    return success_response(
        message="Email verified successfully",
        data={
            "id": verified_user.id,
            "email": verified_user.email,
            "is_email_verified": (verified_user.is_email_verified),
        },
    )


@router.post("/users/resend-verification")
@limiter.limit("3/minute")
def resend_verification(
    request: Request,
    resend_data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        resend_data.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    updated_user = create_new_verification_token(
        db,
        user,
    )

    create_activity_log(
        db=db,
        user_email=updated_user.email,
        action="VERIFICATION_TOKEN_RESENT",
        description=("New email verification token generated"),
    )

    return success_response(
        message=("New verification token generated " "successfully"),
        data={
            "email": updated_user.email,
            "verification": {
                "token": (updated_user.email_verification_token),
                "expires_at": (updated_user.email_verification_expires_at),
            },
        },
    )


@router.post("/users/forgot-password")
@limiter.limit("3/minute")
def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        forgot_data.email,
    )

    generic_message = (
        "If an account exists for this email, "
        "password reset instructions have been generated."
    )

    if user is None:
        return success_response(
            message=generic_message,
            data=None,
        )

    if not user.is_active:
        return success_response(
            message=generic_message,
            data=None,
        )

    updated_user = create_password_reset_token(
        db,
        user,
    )

    create_activity_log(
        db=db,
        user_email=updated_user.email,
        action="PASSWORD_RESET_REQUESTED",
        description=("Password reset token generated successfully"),
    )

    return success_response(
        message=generic_message,
        data={
            "email": updated_user.email,
            "reset": {
                "token": updated_user.password_reset_token,
                "expires_at": (updated_user.password_reset_expires_at),
            },
        },
    )


@router.post("/users/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_password_reset_token(
        db,
        reset_data.token,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token",
        )

    expires_at = user.password_reset_expires_at

    if expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has no expiry",
        )

    if expires_at < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired",
        )

    updated_user = reset_user_password(
        db=db,
        user=user,
        new_password=reset_data.new_password,
    )

    create_activity_log(
        db=db,
        user_email=updated_user.email,
        action="PASSWORD_RESET_COMPLETED",
        description="User password reset successfully",
    )

    return success_response(
        message="Password reset successfully",
        data={
            "email": updated_user.email,
        },
    )


@router.post("/users/login")
@limiter.limit("5/minute")
def login(
    user: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    db_user = authenticate_user(
        db,
        user.email,
        user.password,
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not db_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Email is not verified. " "Please verify your email first."),
        )

    access_token = create_access_token(db_user.email)
    refresh_token = create_refresh_token(db_user.email)

    user_agent = get_user_agent(request)
    ip_address = get_client_ip(request)
    device_name = get_device_name(user_agent)

    created_session = create_session(
        db=db,
        user_email=db_user.email,
        refresh_token=refresh_token,
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    create_activity_log(
        db=db,
        user_email=db_user.email,
        action="LOGIN",
        description=(f"User logged in from {device_name} " f"with IP {ip_address}"),
    )

    return success_response(
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "full_name": db_user.full_name,
                "email": db_user.email,
                "role": db_user.role,
                "is_active": db_user.is_active,
                "is_email_verified": (db_user.is_email_verified),
                "profile_image": db_user.profile_image,
            },
            "session": {
                "id": created_session.id,
                "device_name": (created_session.device_name),
                "ip_address": (created_session.ip_address),
                "created_at": (created_session.created_at),
            },
        },
    )


@router.post("/users/refresh")
@limiter.limit("10/minute")
def refresh_access_token(
    request: Request,
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    if is_token_revoked(
        db,
        token_data.refresh_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    email = decode_refresh_token(token_data.refresh_token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = get_user_by_email(
        db,
        email,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified",
        )

    user_session = get_session_by_refresh_token(
        db,
        token_data.refresh_token,
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found",
        )

    if not user_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is inactive",
        )

    updated_session = update_session_activity(
        db,
        user_session,
    )

    new_access_token = create_access_token(user.email)

    create_activity_log(
        db=db,
        user_email=user.email,
        action="TOKEN_REFRESH",
        description="New access token generated",
    )

    return success_response(
        message="Access token refreshed successfully",
        data={
            "access_token": new_access_token,
            "refresh_token": None,
            "token_type": "bearer",
            "session": {
                "id": updated_session.id,
                "last_activity": (updated_session.last_activity),
            },
        },
    )


@router.post("/users/logout")
@limiter.limit("10/minute")
def logout(
    request: Request,
    token_data: LogoutRequest,
    db: Session = Depends(get_db),
):
    if is_token_revoked(
        db,
        token_data.refresh_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already revoked",
        )

    email = decode_refresh_token(token_data.refresh_token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_session = get_session_by_refresh_token(
        db,
        token_data.refresh_token,
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if not user_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already closed",
        )

    closed_session = close_session(
        db,
        user_session,
    )

    revoke_token(
        db,
        token_data.refresh_token,
    )

    create_activity_log(
        db=db,
        user_email=email,
        action="LOGOUT",
        description=(f"User logged out from " f"{closed_session.device_name}"),
    )

    return success_response(
        message="Logout successful",
        data={
            "session_id": closed_session.id,
            "device_name": closed_session.device_name,
            "logged_out_at": (closed_session.logged_out_at),
        },
    )
