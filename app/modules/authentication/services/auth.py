from ....core.database.dependencies import DBSessionDep
from ....core.database.models import Token, User
from ....core.database.schemas import UserCreate, UserInDB
from ..exceptions import AlreadyRegisteredException, UnauthorizedException
from ..dependencies import AuthHeaderDep
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from ....core.database.services import TokenService, UserService
from .password import PasswordService
from uuid import UUID


class AuthService:
    def __init__(self, session: DBSessionDep):
        self.password_service = PasswordService()
        self.token_service = TokenService(session)
        self.user_service = UserService(session)

    async def register_user(self, user: UserCreate) -> User:
        if await self.user_service.get_user(user.email):
            raise AlreadyRegisteredException
        hashed_password = await self.password_service.get_password_hash(user.password)

        return await self.user_service.create(
            UserInDB(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password,
            )
        )

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> Token:
        if not (user := await self.user_service.get_user(form_data.username)):
            raise UnauthorizedException
        if not await self.password_service.verify_password(
            form_data.password, user.hashed_password
        ):
            raise UnauthorizedException
        return await self.token_service.create_access_token(user, expires_delta=None)

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> User:
        if credentials.scheme != "Bearer":
            raise UnauthorizedException
        if not (token := credentials.credentials):
            raise UnauthorizedException

        payload = self.token_service.decode(token)

        jti = payload.get("jti")
        if not jti or not await self.token_service.validate(UUID(jti)):
            raise UnauthorizedException
        if not (email := payload.get("email")):
            raise UnauthorizedException
        if not (user := await self.user_service.get_user(email)):
            raise UnauthorizedException
        return user

    async def logout(self, credentials: AuthHeaderDep) -> None:
        payload = self.token_service.decode(credentials.credentials)
        await self.token_service.deactivate(UUID(payload.get("jti")))

    async def reset_password():
        pass
