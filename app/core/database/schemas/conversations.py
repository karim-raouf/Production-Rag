from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4


class ConversationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    title: str
    model_type: str


# Schema for API request (client doesn't need to provide user_id)
class ConversationCreateRequest(ConversationBase):
    pass


# Schema for internal use (includes user_id from authenticated user)
class ConversationCreate(ConversationBase):
    user_id: UUID4


class ConversationUpdate(ConversationBase):
    pass


class ConversationOut(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
