from pydantic import BaseModel


class SystemInfoCreate(BaseModel):
    system_name: str
    version: str


class SystemInfoResponse(BaseModel):
    id: int
    system_name: str
    version: str

    model_config = {"from_attributes": True}
