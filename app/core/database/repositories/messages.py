from .interfaces import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Message
from ..schemas import MessageCreate, MessageUpdate
from sqlalchemy import select
from collections.abc import Sequence


class MessageRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int, take: int) -> Sequence[Message]:
        query = select(Message).offset(skip).limit(take)
        return self.session.scalars(query).all()

    async def get(self, message_id: int) -> Message | None:
        return await self.session.get(Message, message_id)

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
        self.session.delete(message)
        await self.session.commit()
