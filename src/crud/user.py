from datetime import timedelta

from src.core.datetime_utils import utc_now
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from src.core.security import hash_password, verify_password
from src.database.models import User
from src.schemas.user import UserCreate

EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30


def get_user_by_email(
    db: Session,
    email: str,
):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(
    db: Session,
    user_id: int,
):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_verification_token(
    db: Session,
    token: str,
):
    return db.query(User).filter(User.email_verification_token == token).first()


def get_user_by_password_reset_token(
    db: Session,
    token: str,
):
    return db.query(User).filter(User.password_reset_token == token).first()


def get_all_users(
    db: Session,
):
    return db.query(User).order_by(User.id.asc()).all()


def generate_secure_token() -> str:
    return token_urlsafe(32)


def create_user(
    db: Session,
    user: UserCreate,
):
    verification_token = generate_secure_token()

    verification_expires_at = utc_now() + timedelta(
        hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user",
        is_email_verified=False,
        email_verification_token=verification_token,
        email_verification_expires_at=(verification_expires_at),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


def update_user_profile(
    db: Session,
    user: User,
    full_name: str,
    email: str,
):
    user.full_name = full_name
    user.email = email

    db.commit()
    db.refresh(user)

    return user


def change_user_password(
    db: Session,
    user: User,
    new_password: str,
):
    user.hashed_password = hash_password(new_password)

    db.commit()
    db.refresh(user)

    return user


def create_new_verification_token(
    db: Session,
    user: User,
):
    user.email_verification_token = generate_secure_token()

    user.email_verification_expires_at = utc_now() + timedelta(
        hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    )

    db.commit()
    db.refresh(user)

    return user


def verify_user_email(
    db: Session,
    user: User,
):
    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_expires_at = None

    db.commit()
    db.refresh(user)

    return user


def create_password_reset_token(
    db: Session,
    user: User,
):
    user.password_reset_token = generate_secure_token()

    user.password_reset_expires_at = utc_now() + timedelta(
        minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )

    db.commit()
    db.refresh(user)

    return user


def reset_user_password(
    db: Session,
    user: User,
    new_password: str,
):
    user.hashed_password = hash_password(new_password)

    user.password_reset_token = None
    user.password_reset_expires_at = None

    db.commit()
    db.refresh(user)

    return user


def clear_password_reset_token(
    db: Session,
    user: User,
):
    user.password_reset_token = None
    user.password_reset_expires_at = None

    db.commit()
    db.refresh(user)

    return user


def update_user_role(
    db: Session,
    user: User,
    role: str,
):
    user.role = role

    db.commit()
    db.refresh(user)

    return user


def update_user_status(
    db: Session,
    user: User,
    is_active: bool,
):
    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user: User,
):
    db.delete(user)
    db.commit()
