from .interfaces import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Message, Conversation
from ..schemas import MessageCreate, MessageUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from collections.abc import Sequence
from pydantic import UUID4


class MessageRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, user_id: UUID4, skip: int, take: int) -> Sequence[Message]:
        query = (
            select(Message)
            .where(Message.conversation.has(Conversation.user_id == user_id))
            .offset(skip)
            .limit(take)
        )
        result = await self.session.scalars(query)
        return result.all()

    async def get(self, message_id: int) -> Message | None:
        query = (
            select(Message)
            .where(Message.id == message_id)
            .options(selectinload(Message.conversation))
        )
        result = await self.session.scalars(query)
        return result.first()

    async def create(self, message: MessageCreate) -> Message:
        new_message = Message(**message.model_dump())
        self.session.add(new_message)
        await self.session.commit()
        await self.session.refresh(new_message)
        return new_message

    async def update(self, message: Message, updated_message: MessageUpdate) -> Message:
        for key, value in updated_message.model_dump(exclude_unset=True).items():
            setattr(message, key, value)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete(self, message: Message) -> None:
        await self.session.delete(message)
        await self.session.commit()
