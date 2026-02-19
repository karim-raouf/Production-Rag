from typing import Annotated
from fastapi import Depends, HTTPException, status

from ...models import Conversation
from ...services import ConversationService
from ...dependencies import DBSessionDep
from .....modules.auth.exceptions import UnauthorizedException
from .....modules.auth.dependencies import CurrentUserDep


async def get_conversation(
    conversation_id: int, session: DBSessionDep, current_user: CurrentUserDep
) -> Conversation:
    if not (conversation := await ConversationService(session).get(conversation_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found"
        )
    if conversation.user_id != current_user.id:
        raise UnauthorizedException
    return conversation


GetConversationDep = Annotated[Conversation, Depends(get_conversation)]
