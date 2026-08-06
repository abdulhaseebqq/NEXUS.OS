from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.responses import success_response
from src.crud.system import (
    create_system,
    delete_system,
    get_all_systems,
    update_system,
)
from src.database.database import get_db
from src.schemas.system import SystemInfoCreate

router = APIRouter()


def serialize_system(system) -> dict:
    return {
        "id": system.id,
        "system_name": system.system_name,
        "version": system.version,
    }


@router.post(
    "/system",
    status_code=status.HTTP_201_CREATED,
)
def create_system_api(
    system: SystemInfoCreate,
    db: Session = Depends(get_db),
):
    created_system = create_system(
        db,
        system,
    )

    return success_response(
        message="System created successfully",
        data=serialize_system(created_system),
    )


@router.get("/system")
def get_systems_api(
    db: Session = Depends(get_db),
):
    systems = get_all_systems(db)

    return success_response(
        message="Systems retrieved successfully",
        data=[serialize_system(system) for system in systems],
    )


@router.put("/system/{system_id}")
def update_system_api(
    system_id: int,
    system: SystemInfoCreate,
    db: Session = Depends(get_db),
):
    updated_system = update_system(
        db,
        system_id,
        system,
    )

    if updated_system is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found",
        )

    return success_response(
        message="System updated successfully",
        data=serialize_system(updated_system),
    )


@router.delete("/system/{system_id}")
def delete_system_api(
    system_id: int,
    db: Session = Depends(get_db),
):
    deleted_system = delete_system(
        db,
        system_id,
    )

    if deleted_system is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found",
        )

    return success_response(
        message="System deleted successfully",
        data={
            "deleted_system_id": system_id,
        },
    )
