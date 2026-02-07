import secrets
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()
username_bytes = b"karim"
password_bytes = b"karim"

async def authenticate_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("UTF-8"),
        username_bytes
    )

    is_password_correct = secrets.compare_digest(
        credentials.password.encode("UTF-8"),
        password_bytes
    )

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate" : "Basic"}
        )
    return credentials.username

AuthenticatedUserDep = Annotated[str, Depends(authenticate_user)]
    


