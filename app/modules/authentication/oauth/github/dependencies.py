from typing import Annotated
import aiohttp
from fastapi import Depends, HTTPException, status, Request
from loguru import logger
from fastapi.security import APIKeyCookie

client_id = "your_client_id"
client_secret = "your_client_secret"

# exchanging the auth_code with the access token from github------------------------

async def exchange_grant_with_access_token(code: str) -> str:
    try:
        body = {
            "client_id" : client_id,
            "client_secret" : client_secret,
            "code" : code
        }

        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://github.com/login/oauth/access_token",
                json = body,
                headers = headers
            ) as resp:
                access_token_data = await resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch the access token. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch access token"
        )
    if not access_token_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to obtain access token"
        )
    return access_token_data.get("access_token", "")


ExchangeCodeTokenDep = Annotated[str, Depends(exchange_grant_with_access_token)]



# CHECKING THE CSRF DEPENDENCY----------------------------------------------

def check_csrf_state(request: Request, state: str) -> None:
    session_state = request.session.get("x-csrf-state-token")
    if not session_state or state != session_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad Request"
        )


# GETTING THE USER INFO FROM GITHUB DEPENDENCY------------------------------------
def get_acces_token(request: Request):
    return request.session.get("access_token")
    
AccesTokenCookie = Annotated[str, Depends(get_acces_token)]


async def get_user_info(access_token = AccesTokenCookie):
    try:
        
        header = {
            "Authorization" :f"Bearer {access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/user",
                headers = header
            ) as resp:
                return await resp.json()   
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"failed to obtain user info {e}"
        )

GetUserInfoDep = Annotated[dict, Depends(get_user_info)]