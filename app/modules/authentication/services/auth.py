from typing import Annotated
from ....core.database.dependencies import DBSessionDep
from ....core.database.models import Token, User
from ....core.database.schemas import UserCreate, UserInDB
from ..exceptions import AlreadyRegisteredException, UnauthorizedException
from fastapi import Depends
from ..dependencies import LoginFormDep, AuthHeaderDep
from ....core.database.services import TokenService, UserService
from .password import PasswordService



class AuthService:
    def __init__(self, session: DBSessionDep):
        self.password_service = PasswordService()
        self.token_service = TokenService(session)
        self.user_service = UserService(session)

    async def register_user():
        pass

    async def authenticate_user():
        pass

    async def get_current_user():
        pass

    async def logout():
        pass
