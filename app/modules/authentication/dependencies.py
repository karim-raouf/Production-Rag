from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm
)
from fastapi import Depends
from typing import Annotated

# it checks the incoming request for a authorization header that is Bearer type ( Authorization: Bearer <Token> ) 
security = HTTPBearer()

# this dependency look for field names username and password in the formdata in request (used in login endpoint)
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# dependency that check that the incoming request have JWT Bearer token (used to secure endpoints)
AuthHeaderDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]
