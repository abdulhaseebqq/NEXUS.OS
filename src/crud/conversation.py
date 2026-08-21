from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.datetime_utils import utc_now
from src.database.models import Conversation, Message


def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New conversation",
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
        )
        .order_by(
            Conversation.updated_at.desc(),
        )
    )

    return list(
        db.scalars(statement).all(),
    )


def get_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation | None:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )

    return db.scalar(statement)


def rename_conversation(
    db: Session,
    conversation: Conversation,
    title: str,
) -> Conversation:
    conversation.title = title
    conversation.updated_at = utc_now()

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    conversation: Conversation,
) -> None:
    db.delete(conversation)
    db.commit()


def create_message(
    db: Session,
    conversation: Conversation,
    role: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
    )

    conversation.updated_at = utc_now()

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
        )
        .order_by(Message.id.asc())
    )

    return list(
        db.scalars(statement).all(),
    )
