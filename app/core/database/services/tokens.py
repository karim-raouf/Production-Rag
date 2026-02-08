from datetime import UTC, datetime, timedelta
from ....modules.authentication.exceptions import UnauthorizedException
from jose import JWTError, jwt
from ..repositories import TokenRepository
from ..schemas import TokenCreate, TokenUpdate
import uuid

class TokenService(TokenRepository):
    secret_key = "your_secret_key"
    algorithm = "HS256"
    expires_in_minutes = 60

    async def create_access_token(
        self,
        data: dict,
        expires_delta: timedelta | None
    ) -> str:
        to_encode = data.copy
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.expires_in_minutes)
        
        token = self.create(TokenCreate(expires_at=expire))
        to_encode.update(
            {"exp":expire, "iss":"AuthService", "sub":token.id}
        )
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    async def deactivate(
        self, 
        token_id: uuid.UUID
    ) -> None:
        await self.update(token_id, TokenUpdate(is_active=False))

    def decode(
        self, 
        encoded_token: str
    ) -> dict:
        try:
            return jwt.decode(
                encoded_token, self.secret_key, algorithm=[self.algorithm]
            )
        except JWTError:
            raise UnauthorizedException

    async def validate(
        self,
        token_id: uuid.UUID
    ):
        return (token := self.get(token_id)) is not None and token.is_active