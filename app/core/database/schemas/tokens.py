from datetime import datetime
from pydantic import BaseModel, IPvAnyAddress, field_serializer
import uuid


class TokenBase(BaseModel):
    user_id: uuid.uuid4
    expires_at: datetime
    is_active: bool = True
    ip_address: IPvAnyAddress | None = None

    @field_serializer("ip_address")
    def serialize_ip(
        self, 
        ip: IPvAnyAddress | None
    ) -> str | None:
        return str(ip) if ip else None


class TokenCreate(TokenBase):
    pass

class TokenUpdate(TokenBase):
    pass

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"