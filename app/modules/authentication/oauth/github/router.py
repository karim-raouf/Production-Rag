import secrets
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import RedirectResponse
from .dependencies import check_csrf_state, ExchangeCodeTokenDep

client_id = "your_client_id"
client_secret = "your_client_secret"


router = APIRouter()


@router.get("/oauth/github/login")
async def oauth_github_login_controller(request: Request) -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    request.session["x-csrf-state-token"] = state
    redirect_uri = request.url_for("oauth_github_callback_controller")
    response = RedirectResponse(
        url=f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"?redirect_uri={redirect_uri}"
        f"?state={state}"
        f"?scope=user"
    )
    return response

@router.get("/oauth/github/callback", dependencies=[Depends(check_csrf_state)])
async def oauth_github_callback_controller(
    access_token = ExchangeCodeTokenDep
):
    response = RedirectResponse(url="http://localhost:8501")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False, # turn true in production,
        samesite="lax"
    )
    return  response
