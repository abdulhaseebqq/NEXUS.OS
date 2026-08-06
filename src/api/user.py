from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_password,
)
from src.crud.activity import create_activity_log
from src.crud.session import (
    close_all_active_sessions,
    close_session,
    create_session,
    get_active_sessions,
    get_session_by_id,
    get_session_by_refresh_token,
    update_session_activity,
)
from src.crud.token import (
    is_token_revoked,
    revoke_token,
)
from src.crud.user import (
    authenticate_user,
    change_user_password,
    create_user,
    get_user_by_email,
    update_user_profile,
)
from src.database.database import get_db
from src.schemas.session import SessionResponse
from src.schemas.user import (
    LogoutRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserProfileUpdate,
    UserResponse,
)

router = APIRouter()
bearer_scheme = HTTPBearer()


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROFILE_IMAGES_DIRECTORY = PROJECT_ROOT / "uploads" / "profile_images"

PROFILE_IMAGES_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
):
    email = decode_access_token(credentials.credentials)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


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
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
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
        description="User account created successfully",
    )

    return created_user


@router.post("/users/login")
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

    access_token = create_access_token(db_user.email)
    refresh_token = create_refresh_token(db_user.email)

    user_agent = get_user_agent(request)
    ip_address = get_client_ip(request)
    device_name = get_device_name(user_agent)

    create_session(
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "profile_image": db_user.profile_image,
        },
    }


@router.post(
    "/users/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    if is_token_revoked(
        db,
        request.refresh_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    email = decode_refresh_token(request.refresh_token)

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

    user_session = get_session_by_refresh_token(
        db,
        request.refresh_token,
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

    update_session_activity(
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

    return {
        "access_token": new_access_token,
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.post("/users/logout")
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
):
    if is_token_revoked(
        db,
        request.refresh_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already revoked",
        )

    email = decode_refresh_token(request.refresh_token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_session = get_session_by_refresh_token(
        db,
        request.refresh_token,
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

    close_session(
        db,
        user_session,
    )

    revoke_token(
        db,
        request.refresh_token,
    )

    create_activity_log(
        db=db,
        user_email=email,
        action="LOGOUT",
        description=(f"User logged out from " f"{user_session.device_name}"),
    )

    return {
        "message": "Logout successful",
    }


@router.get(
    "/users/me",
    response_model=UserResponse,
)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    return get_authenticated_user(
        credentials,
        db,
    )


@router.put(
    "/users/me",
    response_model=UserResponse,
)
def update_current_user_profile(
    profile_data: UserProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
        credentials,
        db,
    )

    existing_user = get_user_by_email(
        db,
        profile_data.email,
    )

    if existing_user is not None and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    old_email = current_user.email
    old_name = current_user.full_name

    updated_user = update_user_profile(
        db=db,
        user=current_user,
        full_name=profile_data.full_name,
        email=profile_data.email,
    )

    create_activity_log(
        db=db,
        user_email=updated_user.email,
        action="PROFILE_UPDATED",
        description=(
            f"Profile updated from name '{old_name}' " f"and email '{old_email}'"
        ),
    )

    return updated_user


@router.put("/users/me/password")
def update_current_user_password(
    password_data: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
        credentials,
        db,
    )

    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    change_user_password(
        db=db,
        user=current_user,
        new_password=password_data.new_password,
    )

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="PASSWORD_CHANGED",
        description="User password changed successfully",
    )

    return {
        "message": "Password changed successfully",
    }


@router.post(
    "/users/me/profile-image",
    response_model=UserResponse,
)
async def upload_profile_image(
    image: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
        credentials,
        db,
    )

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed",
        )

    image_content = await image.read()

    if not image_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty",
        )

    if len(image_content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile image must not exceed 5 MB",
        )

    file_extension = ALLOWED_IMAGE_TYPES[image.content_type]

    unique_filename = f"user_{current_user.id}_{uuid4().hex}" f"{file_extension}"

    image_path = PROFILE_IMAGES_DIRECTORY / unique_filename

    try:
        image_path.write_bytes(image_content)
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save profile image",
        )

    old_profile_image = current_user.profile_image

    if old_profile_image:
        old_filename = Path(old_profile_image).name
        old_image_path = PROFILE_IMAGES_DIRECTORY / old_filename

        if old_image_path.exists():
            try:
                old_image_path.unlink()
            except OSError:
                pass

    current_user.profile_image = f"/uploads/profile_images/{unique_filename}"

    db.commit()
    db.refresh(current_user)

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="PROFILE_IMAGE_UPDATED",
        description="User profile image updated successfully",
    )

    return current_user


@router.get(
    "/users/me/sessions",
    response_model=list[SessionResponse],
)
def list_current_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
        credentials,
        db,
    )

    return get_active_sessions(
        db,
        current_user.email,
    )


@router.delete("/users/me/sessions")
def close_all_current_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
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

    return {
        "message": "All sessions closed successfully",
        "closed_sessions": len(closed_sessions),
        "revoked_tokens": revoked_count,
    }


@router.delete("/users/me/sessions/{session_id}")
def close_current_user_session(
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
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

    close_session(
        db,
        user_session,
    )

    if not is_token_revoked(
        db,
        user_session.refresh_token,
    ):
        revoke_token(
            db,
            user_session.refresh_token,
        )

    create_activity_log(
        db=db,
        user_email=current_user.email,
        action="SESSION_CLOSED",
        description=(
            f"Closed session ID {user_session.id} " f"on {user_session.device_name}"
        ),
    )

    return {
        "message": "Session closed successfully",
        "session_id": user_session.id,
        "device_name": user_session.device_name,
    }
