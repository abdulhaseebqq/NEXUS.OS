from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.core.dependencies import get_current_active_user
from src.core.responses import success_response
from src.crud.conversation import (
    create_conversation,
    create_message,
    delete_conversation,
    get_conversation,
    get_conversation_messages,
    get_user_conversations,
    rename_conversation,
)
from src.database.database import get_db
from src.database.models import User
from src.schemas.chat import (
    ConversationCreateRequest,
    ConversationRenameRequest,
    MessageCreateRequest,
)
from src.services.ai import (
    AIServiceError,
    generate_ai_response,
)

router = APIRouter()


def serialize_conversation(
    conversation,
) -> dict:
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


def serialize_message(
    message,
) -> dict:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
    }


@router.post("/chat/conversations")
def create_new_conversation(
    payload: ConversationCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    title = payload.title.strip() if payload.title else "New conversation"

    conversation = create_conversation(
        db=db,
        user_id=current_user.id,
        title=title,
    )

    return success_response(
        message="Conversation created successfully",
        data=serialize_conversation(conversation),
    )


@router.get("/chat/conversations")
def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversations = get_user_conversations(
        db,
        current_user.id,
    )

    return success_response(
        message="Conversations retrieved successfully",
        data=[serialize_conversation(conversation) for conversation in conversations],
    )


@router.get("/chat/conversations/{conversation_id}")
def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation(
        db,
        conversation_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = get_conversation_messages(
        db,
        conversation.id,
    )

    return success_response(
        message="Conversation retrieved successfully",
        data={
            "conversation": (serialize_conversation(conversation)),
            "messages": [serialize_message(message) for message in messages],
        },
    )


@router.patch("/chat/conversations/{conversation_id}")
def update_conversation_title(
    conversation_id: int,
    payload: ConversationRenameRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation(
        db,
        conversation_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    conversation = rename_conversation(
        db,
        conversation,
        payload.title.strip(),
    )

    return success_response(
        message="Conversation renamed successfully",
        data=serialize_conversation(conversation),
    )


@router.delete("/chat/conversations/{conversation_id}")
def remove_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation(
        db,
        conversation_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    delete_conversation(
        db,
        conversation,
    )

    return success_response(
        message="Conversation deleted successfully",
        data=None,
    )


@router.post("/chat/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation(
        db,
        conversation_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    content = payload.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    user_message = create_message(
        db=db,
        conversation=conversation,
        role="user",
        content=content,
    )

    if conversation.title == "New conversation":
        conversation = rename_conversation(
            db,
            conversation,
            content[:60],
        )

    try:
        ai_content = generate_ai_response(content)
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    assistant_message = create_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=ai_content,
    )

    return success_response(
        message="Message processed successfully",
        data={
            "conversation": (serialize_conversation(conversation)),
            "user_message": (serialize_message(user_message)),
            "assistant_message": (serialize_message(assistant_message)),
        },
    )
