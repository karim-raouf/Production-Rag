from loguru import logger
from ....core.database.dependencies import DBSessionDep
from ....core.database.models import Token, User
from ....core.database.schemas import UserCreate, UserInDB
from ..exceptions import AlreadyRegisteredException, UnauthenticatedException
from fastapi.security import OAuth2PasswordRequestForm
from ....core.database.services import TokenService, UserService
from .password import PasswordService
from uuid import UUID


class AuthService:
    def __init__(self, session: DBSessionDep):
        self.password_service = PasswordService()
        self.token_service = TokenService(session)
        self.user_service = UserService(session)

    async def register_user(self, user: UserCreate) -> User:
        if await self.user_service.get_user_by_email(user.email):
            raise AlreadyRegisteredException
        hashed_password = await self.password_service.get_password_hash(user.password)

        return await self.user_service.create(
            UserInDB(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password,
                github_id=user.github_id,
            )
        )

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> Token:
        if not (user := await self.user_service.get_user_by_email(form_data.username)):
            logger.error(
                f"authenticate_user: User not found with email '{form_data.username}'"
            )
            raise UnauthenticatedException
        if not await self.password_service.verify_password(
            form_data.password, user.hashed_password
        ):
            logger.error(
                f"authenticate_user: Invalid password for user '{form_data.username}'"
            )
            raise UnauthenticatedException
        return await self.token_service.create_access_token(user, expires_delta=None)

    async def get_current_user(self, token: str) -> User:
        if not token:
            logger.error("get_current_user: Empty token")
            raise UnauthenticatedException

        payload = self.token_service.decode(token)

        jti = payload.get("jti")
        if not jti or not await self.token_service.validate(UUID(jti)):
            logger.error(f"get_current_user: Invalid or missing jti '{jti}'")
            raise UnauthenticatedException
        if not (email := payload.get("email")):
            logger.error("get_current_user: Missing email in token payload")
            raise UnauthenticatedException
        if not (user := await self.user_service.get_user_by_email(email)):
            logger.error(f"get_current_user: User not found for email '{email}'")
            raise UnauthenticatedException
        return user

    async def logout(self, token: str) -> None:
        payload = self.token_service.decode(token)
        await self.token_service.deactivate(UUID(payload.get("jti")))

    async def reset_password():
        pass
