from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from ...core.database.dependencies import DBSessionDep
from .services import AuthService

# it checks the incoming request for a authorization header that is Bearer type ( Authorization: Bearer <Token> )
# auto_error=False allows us to check cookies if header is missing
security = HTTPBearer(auto_error=False)

# this dependency look for field names username and password in the formdata in request (used in login endpoint)
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_token_from_header_or_cookie(
    request: Request, creds: HTTPAuthorizationCredentials | None = Depends(security)
) -> str:
    """
    Extracts the token from the Authorization header or the 'access_token' cookie.
    Prioritizes the header.
    """
    if creds:
        return creds.credentials

    token = request.cookies.get("access_token")
    if token:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Dependency that provides the raw token string
AuthTokenDep = Annotated[str, Depends(get_token_from_header_or_cookie)]


async def get_current_user_dep(token: AuthTokenDep, session: DBSessionDep):
    auth_service = AuthService(session)
    return await auth_service.get_current_user(token)
