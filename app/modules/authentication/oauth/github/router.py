import secrets
from fastapi import APIRouter, Request, Depends
from loguru import logger
from fastapi.responses import RedirectResponse
from .dependencies import check_csrf_state, ExchangeCodeTokenDep, GetUserInfoDep

from ..config import GITHUB_CLIENT_ID


router = APIRouter()


@router.get("/github/login")
async def oauth_github_login_controller(request: Request) -> RedirectResponse:
    logger.info("Initiating GitHub OAuth login.")
    state = secrets.token_urlsafe(16)
    request.session["x-csrf-state-token"] = state
    redirect_uri = request.url_for("oauth_github_callback_controller")
    response = RedirectResponse(
        url=f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope=user"
    )
    return response


@router.get("/github/callback", dependencies=[Depends(check_csrf_state)])
async def oauth_github_callback_controller(
    request: Request, access_token: ExchangeCodeTokenDep
):
    logger.info(f"GitHub OAuth callback received. Access token: {access_token}")
    request.session["access_token"] = access_token
    response = RedirectResponse(url="http://127.0.0.1:8080")
    return response


@router.get("/github/users/me")
async def get_current_user_controller(user_info: GetUserInfoDep):
    logger.info(f"Returning current user info: {user_info}")
    return user_info
