from ...dependencies import DBSessionDep
from ...repositories import MessageRepository
from ...models import Message
from typing import Annotated
from fastapi import Depends, HTTPException, status
from .....modules.auth.exceptions import UnauthorizedException
from .....modules.auth.dependencies import CurrentUserDep


async def get_message(
    session: DBSessionDep, current_user: CurrentUserDep, message_id: int
) -> Message:
    if not (message := await MessageRepository(session).get(message_id=message_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="message not found"
        )
    if message.conversation.user_id != current_user.id:
        raise UnauthorizedException

    return message


GetMessageDep = Annotated[Message, Depends(get_message)]
