from fastapi import APIRouter, status

from ...schemas import (
    ConversationOut,
    ConversationCreate,
    ConversationCreateRequest,
    ConversationUpdate,
    MessageOut,
)
from ...services import ConversationService
from ...dependencies import DBSessionDep
from .dependencies import GetConversationDep
from app.modules.auth.dependencies import CurrentUserDep
app = APIRouter(prefix="/conversations")




@app.get("")
async def list_conversation_controller(
    current_user: CurrentUserDep,
    session: DBSessionDep, 
    skip: int = 0, 
    take: int = 100
) -> list[ConversationOut]:
    conversations = await ConversationService(session).get_all(
        user_id=current_user.id, 
        skip=skip, 
        take=take
    )
    return [ConversationOut.model_validate(c) for c in conversations]


@app.get("/{conversation_id}")
async def get_conversation_controller(
    conversation: GetConversationDep,
) -> ConversationOut:
    return ConversationOut.model_validate(conversation)



@app.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation_controller(
    session: DBSessionDep,
    current_user: CurrentUserDep,
    conversation: ConversationCreateRequest,
) -> ConversationOut:
    # Inject user_id from authenticated user
    conversation_with_user = ConversationCreate(
        **conversation.model_dump(), user_id=current_user.id
    )
    new_conversation = await ConversationService(session).create(conversation_with_user)
    return ConversationOut.model_validate(new_conversation)


@app.put("/{conversation_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_conversation_controller(
    session: DBSessionDep,
    conversation: GetConversationDep,
    updated_conversation: ConversationUpdate,
) -> ConversationOut:
    updated_conversation = await ConversationService(session).update(
        conversation, updated_conversation, 
    )
    return ConversationOut.model_validate(updated_conversation)


@app.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_controller(
    session: DBSessionDep, 
    conversation: GetConversationDep, 
) -> None:
    await ConversationService(session).delete(conversation)


@app.get("/{conversation_id}/messages")
async def get_conversation_messages_controller(
    session: DBSessionDep, 
    conversation: GetConversationDep,
) -> list[MessageOut]:
    messages = await ConversationService(session).list_messages(conversation.id)
    return [MessageOut.model_validate(m) for m in messages]
