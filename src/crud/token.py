from sqlalchemy.orm import Session

from src.database.models import RevokedToken


def revoke_token(
    db: Session,
    token: str,
) -> RevokedToken:
    revoked_token = RevokedToken(
        token=token,
    )

    db.add(revoked_token)
    db.commit()
    db.refresh(revoked_token)

    return revoked_token


def is_token_revoked(
    db: Session,
    token: str,
) -> bool:
    revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()

    return revoked_token is not None
