from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import DATABASE_URL
from src.database.base import Base

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_tables():
    from src.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
