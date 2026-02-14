import secrets
from fastapi import APIRouter, Request, Depends
from loguru import logger
from fastapi.responses import RedirectResponse
from .dependencies import check_csrf_state, ExchangeCodeTokenDep, get_user_info
from ..config import GITHUB_CLIENT_ID
from ...dependencies import AuthServiceDep, UserServiceDep, TokenServiceDep
from .....core.database.schemas import UserCreate, UserInDB

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
        f"&scope=user:email"
    )
    return response


@router.get("/github/callback", dependencies=[Depends(check_csrf_state)])
async def oauth_github_callback_controller(
    request: Request,
    access_token: ExchangeCodeTokenDep,
    auth_service: AuthServiceDep,
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
):
    user_info: tuple = await get_user_info(access_token)
    logger.info(f"GitHub OAuth callback received. Access token: {access_token}")
    github_id, github_email, github_username = user_info

    if not (user := await user_service.get_user_by_github_id(str(github_id))):
        if user := await user_service.get_user_by_email(github_email):
            # User exists by email, link account
            user_in = UserInDB.model_validate(user)
            user_in.github_id = str(github_id)
            user = await user_service.update(user.id, user_in)
        else:
            # New user
            random_password = secrets.token_urlsafe(16)
            user = await auth_service.register_user(
                UserCreate(
                    github_id=str(github_id),
                    email=github_email,
                    username=github_username,
                    password=random_password,
                )
            )

    logger.info("Github account logged in")
    token = await token_service.create_access_token(user, expires_delta=None)
    request.session["access_token"] = token
    request.session["token_type"] = "Bearer"
    return RedirectResponse(url="/")


# @router.get("/github/users/app/login")
# async def login_github_user_controller(user_info: GetUserInfoDep):
#     logger.info(f"Returning current user info: {user_info}")
#     return user_info
