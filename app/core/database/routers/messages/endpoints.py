from fastapi import APIRouter, status

from ...schemas import MessageCreate, MessageUpdate, MessageOut

from ...repositories import MessageRepository
from ...dependencies import DBSessionDep
from .dependencies import GetMessageDep


app = APIRouter(prefix="/messages")


@app.get("")
async def list_messages_controller(
    session: DBSessionDep, skip: int = 0, take: int = 25
) -> list[MessageOut]:
    messages = await MessageRepository(session).get_all(skip, take)
    return [MessageOut.model_validate(m) for m in messages]


@app.get("/{message_id}")
async def get_message_controller(conversation: GetMessageDep) -> MessageOut:
    return MessageOut.model_validate(conversation)


@app.post("", status_code=status.HTTP_201_CREATED)
async def create_message_controller(
    session: DBSessionDep, message: MessageCreate
) -> MessageOut:
    new_message = await MessageRepository(session).create(message)
    return MessageOut.model_validate(new_message)


@app.put("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_message_controller(
    session: DBSessionDep, message: GetMessageDep, updated_message: MessageUpdate
) -> MessageOut:
    updated_message = await MessageRepository(session).update(message, updated_message)
    return MessageOut.model_validate(updated_message)


@app.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message_controller(
    session: DBSessionDep, message: GetMessageDep
) -> None:
    await MessageRepository(session).delete(message)
