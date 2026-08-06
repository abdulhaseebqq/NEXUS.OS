from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from src.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except UnknownHashError:
        return False


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + expires_delta

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": issued_at,
        "exp": expires_at,
        "jti": uuid4().hex,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def create_access_token(subject: str) -> str:
    return create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS,
        ),
    )


def decode_token(
    token: str,
    expected_type: str,
) -> str | None:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("type") != expected_type:
            return None

        subject = payload.get("sub")

        if not isinstance(subject, str):
            return None

        return subject

    except JWTError:
        return None


def decode_access_token(token: str) -> str | None:
    return decode_token(
        token=token,
        expected_type="access",
    )


def decode_refresh_token(token: str) -> str | None:
    return decode_token(
        token=token,
        expected_type="refresh",
    )
