from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url_content: str | None = None
    rag_content: str | None = None
    request_content: str
    response_content: str
    conversation_id: int
    prompt_token: int | None = None
    response_token: int | None = None
    total_token: int | None = None
    is_success: bool | None = None
    status_code: int | None = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime
