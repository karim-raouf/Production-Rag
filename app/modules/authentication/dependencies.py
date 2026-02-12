from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from ...core.database.dependencies import DBSessionDep
from .services import AuthService
from ...core.database.services import UserService, TokenService

# it checks the incoming request for a authorization header that is Bearer type ( Authorization: Bearer <Token> )
# auto_error=False allows us to check cookies if header is missing
security = HTTPBearer(auto_error=False)

# this dependency look for field names username and password in the formdata in request (used in login endpoint)
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_token_from_cookie(request: Request) -> str:
    if token := request.session.get("access_token"):
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Dependency that provides the raw token string
AuthTokenDep = Annotated[str, Depends(get_token_from_cookie)]


def get_auth_service(session: DBSessionDep):
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

async def get_current_user_dep(token: AuthTokenDep, auth_service: AuthServiceDep):
    return await auth_service.get_current_user(token)


def get_user_service(session: DBSessionDep):
    return UserService(session)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_token_service(session: DBSessionDep):
    return TokenService(session)

TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]