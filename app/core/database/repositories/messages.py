from .interfaces import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Message
from ..schemas import MessageCreate, MessageUpdate
from sqlalchemy import select


class MessageRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        skip: int,
        take: int
        ) -> list[Message]:
        messages = await self.session.execute(
            select(Message).offset(skip).limit(take)
        )
        return messages.scalars().all()


    async def get(
        self,
        message_id: int
    ) -> Message:
        message = await self.session.execute(
            select(Message).where(Message.id == message_id)
        )
        return message.scalars().first()

    async def create(
        self,
        message: MessageCreate
    ) -> Message:
        new_message = Message(**message.model_dump())
        self.session.add(new_message)
        await self.session.commit()
        await self.session.refresh(new_message)
        return new_message


    async def update(
        self,
        message: Message,
        updated_message: MessageUpdate
    ) -> Message:
        for key, value in updated_message.model_dump().items():
            setattr(message, key, value)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete(
        self,
        message: Message
    ) -> None:
        await self.session.delete(message)
        await self.session.commit()
