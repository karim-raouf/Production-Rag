from loguru import logger
from datetime import UTC, datetime, timedelta
from ....modules.authentication.exceptions import UnauthorizedException
from jose import JWTError, jwt
from ..repositories import TokenRepository
from ..schemas import TokenCreate, TokenUpdate
from pydantic import UUID4
from ...database.models import User
from ...config import get_settings


class TokenService(TokenRepository):
    @property
    def settings(self):
        return get_settings()

    async def create_access_token(
        self, user: User, expires_delta: timedelta | None
    ) -> str:
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.settings.jwt_expires_in_minutes
            )

        token = await self.create(TokenCreate(user_id=user.id, expires_at=expire))

        to_encode = {
            "sub": str(user.id),
            "iat": datetime.now(UTC),
            "iss": "AuthService",
            "jti": str(token.id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )
        return encoded_jwt

    async def deactivate(self, token_id: UUID4) -> None:
        await self.update(token_id, TokenUpdate(is_active=False))

    def decode(self, encoded_token: str) -> dict:
        try:
            return jwt.decode(
                encoded_token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError as e:
            logger.error(f"decode: JWT decode failed - {type(e).__name__}: {e}")
            raise UnauthorizedException

    async def validate(self, token_id: UUID4):
        if not (token := await self.get(token_id)):
            logger.error(f"validate: Token not found with id '{token_id}'")
            raise UnauthorizedException
        if not token.is_active:
            logger.error(f"validate: Token '{token_id}' is inactive/revoked")
            raise UnauthorizedException
        if token.expires_at < datetime.now(UTC):
            logger.error(
                f"validate: Token '{token_id}' has expired at {token.expires_at}"
            )
            await self.deactivate(token.id)
            raise UnauthorizedException

        return True
