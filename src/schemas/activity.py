from datetime import datetime

from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: int
    user_email: str
    action: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}
