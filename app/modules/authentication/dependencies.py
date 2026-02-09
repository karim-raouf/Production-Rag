from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm
)
from fastapi import Depends
from typing import Annotated
from ...core.database.dependencies import DBSessionDep
from .services import AuthService


# it checks the incoming request for a authorization header that is Bearer type ( Authorization: Bearer <Token> ) 
security = HTTPBearer()

# this dependency look for field names username and password in the formdata in request (used in login endpoint)
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# dependency that check that the incoming request have JWT Bearer token (used to secure endpoints)
AuthHeaderDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


async def get_current_user_dep(
    credentials: AuthHeaderDep,
    session: DBSessionDep
):
    auth_service = AuthService(session)
    return await auth_service.get_current_user(credentials)
