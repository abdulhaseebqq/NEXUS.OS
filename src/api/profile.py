from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.core.responses import success_response
from src.core.security import (
    decode_access_token,
    verify_password,
)
from src.crud.activity import create_activity_log
from src.crud.user import (
    change_user_password,
    get_user_by_email,
    update_user_profile,
)
from src.database.database import get_db
from src.schemas.user import (
    PasswordChangeRequest,
    UserProfileUpdate,
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


def serialize_user(user) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "profile_image": user.profile_image,
        "created_at": user.created_at,
    }


@router.get("/users/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    current_user = get_authenticated_user(
        credentials,
        db,
    )

    return success_response(
        message="Profile retrieved successfully",
        data=serialize_user(current_user),
    )


@router.put("/users/me")
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

    return success_response(
        message="Profile updated successfully",
        data=serialize_user(updated_user),
    )


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

    return success_response(
        message="Password changed successfully",
        data=None,
    )


@router.post("/users/me/profile-image")
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

    return success_response(
        message="Profile image updated successfully",
        data=serialize_user(current_user),
    )
