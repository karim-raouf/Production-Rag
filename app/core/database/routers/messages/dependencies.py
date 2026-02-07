from ...dependencies import DBSessionDep
from ...repositories import MessageRepository
from ...models import Message
from typing import Annotated
from fastapi import Depends, HTTPException, status

async def get_message(
    session: DBSessionDep,
    message_id: int
) -> Message:
    if not (message := await MessageRepository(session).get(message_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="message not found"
        )
    return message


GetMessageDep = Annotated[Message, Depends(get_message)]