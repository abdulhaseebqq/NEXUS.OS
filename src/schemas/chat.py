from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=200,
    )


class MessageCreateRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=20000,
    )


class ConversationRenameRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
