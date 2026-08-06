from sqlalchemy.orm import Session

from src.database.models import SystemInfo
from src.schemas.system import SystemInfoCreate


def create_system(db: Session, system: SystemInfoCreate):
    new_system = SystemInfo(system_name=system.system_name, version=system.version)

    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    return new_system


def get_all_systems(db: Session):
    return db.query(SystemInfo).all()


def update_system(db: Session, system_id: int, system: SystemInfoCreate):
    existing_system = db.query(SystemInfo).filter(SystemInfo.id == system_id).first()

    if existing_system is None:
        return None

    existing_system.system_name = system.system_name
    existing_system.version = system.version

    db.commit()
    db.refresh(existing_system)

    return existing_system


def delete_system(db: Session, system_id: int):
    existing_system = db.query(SystemInfo).filter(SystemInfo.id == system_id).first()

    if existing_system is None:
        return None

    db.delete(existing_system)
    db.commit()

    return existing_system
