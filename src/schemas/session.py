from datetime import datetime

from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    user_agent: str
    is_active: bool
    created_at: datetime
    last_activity: datetime
    logged_out_at: datetime | None = None

    model_config = {"from_attributes": True}
