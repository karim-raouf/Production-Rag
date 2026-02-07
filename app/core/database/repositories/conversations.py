from ..models import Conversation
from .interfaces import Repository
from ..schemas.conversations import ConversationCreate, ConversationUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ConversationRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self, 
        skip: int, 
        take: int
    ) -> list[Conversation] | list[None]:
        result = await self.session.execute(
            select(Conversation).offset(skip).limit(take)
        )
        return result.scalars().all()


    async def get(
        self, 
        conversation_id: int
    ) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalars().first()


    async def create(
        self, 
        conversation: ConversationCreate
    ) -> Conversation:
        new_conversation = Conversation(**conversation.model_dump())
        self.session.add(new_conversation)
        await self.session.commit()
        await self.session.refresh(new_conversation)
        return new_conversation

    async def update(
        self, 
        conversation: Conversation, 
        updated_conversation: ConversationUpdate
    ) -> Conversation:
        for key, value in updated_conversation.model_dump().items():
            setattr(conversation, key, value)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation


    async def delete(
        self, 
        conversation: Conversation
    ) -> None:
        await self.session.delete(conversation)
        await self.session.commit()
