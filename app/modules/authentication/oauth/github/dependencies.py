from typing import Annotated
import aiohttp
from fastapi import Depends, HTTPException, status, Request, Query
from loguru import logger

from ..config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET


# exchanging the auth_code with the access token from github------------------------


async def exchange_grant_with_access_token(code: str = Query()) -> str:
    logger.info(f"Exchanging grant code for access token. Code: {code}")
    try:
        body = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        }

        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://github.com/login/oauth/access_token",
                json=body,
                headers=headers,
            ) as resp:
                logger.info(f"Received response from GitHub: {resp.status}")
                access_token_data = await resp.json()
                logger.info(f"Access token data: {access_token_data}")
    except Exception as e:
        logger.warning(f"Failed to fetch the access token. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch access token",
        )
    if not access_token_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to obtain access token",
        )
    return access_token_data.get("access_token", "")


ExchangeCodeTokenDep = Annotated[str, Depends(exchange_grant_with_access_token)]


# CHECKING THE CSRF DEPENDENCY----------------------------------------------


def check_csrf_state(request: Request, state: str) -> None:
    session_state = request.session.get("x-csrf-state-token")
    logger.info(
        f"Checking CSRF state. Session state: {session_state}, Request state: {state}"
    )
    if not session_state or state != session_state:
        logger.warning("CSRF state mismatch or missing.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad Request"
        )


# GETTING THE USER INFO FROM GITHUB DEPENDENCY------------------------------------
# def get_acces_token(request: Request):
#     return request.session.get("access_token")


# AccesTokenCookie = Annotated[str, Depends(get_acces_token)]


async def get_user_info(access_token: str):
    logger.info(f"Fetching user info with access token: {access_token}")
    try:
        header = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/user/emails", headers=header
            ) as email_resp:
                email_data = await email_resp.json()

            async with session.get(
                "https://api.github.com/user", headers=header
            ) as profile_resp:
                profile_data = await profile_resp.json()

            email = next(
                (item["email"] for item in email_data if item["primary"]), None
            )
            github_id, usename = profile_data["id"], profile_data["login"]

            return (github_id, email, usename)

    except Exception as e:
        logger.error(f"Failed to fetch user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"failed to obtain user info {e}",
        )
