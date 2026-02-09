from ..models import Conversation
from .interfaces import Repository
from ..schemas.conversations import ConversationCreate, ConversationUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence


class ConversationRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, skip: int, take: int) -> Sequence[Conversation]:
        query = select(Conversation).offset(skip).limit(take)
        result = await self.session.scalars(query)
        return result.all()

    async def get(self, conversation_id: int) -> Conversation | None:
        return await self.session.get(Conversation, conversation_id)

    async def create(self, conversation: ConversationCreate) -> Conversation:
        new_conversation = Conversation(**conversation.model_dump())
        self.session.add(new_conversation)
        await self.session.commit()
        await self.session.refresh(new_conversation)
        return new_conversation

    async def update(
        self, conversation: Conversation, updated_conversation: ConversationUpdate
    ) -> Conversation:
        for key, value in updated_conversation.model_dump(exclude_unset=True).items():
            setattr(conversation, key, value)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def delete(self, conversation: Conversation) -> None:
        self.session.delete(conversation)
        await self.session.commit()
