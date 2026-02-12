from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ...core.database.schemas import TokenOut, UserOut, UserCreate
from .dependencies import AuthTokenDep, LoginFormDep, AuthServiceDep


router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/register")
async def register_user_controller(
    user: UserCreate, auth_service: AuthServiceDep
) -> UserOut:
    return await auth_service.register_user(user)


@router.post("/token")
async def login_for_access_token_controller(
    request: Request, auth_service: AuthServiceDep, form_data: LoginFormDep
) -> TokenOut:
    token = await auth_service.authenticate_user(form_data)
    request.session["access_token"] = token
    request.session["token_type"] = "Bearer"
    return RedirectResponse(url="/")


@router.post("/logout")
async def logout_access_token_controller(
    request: Request, auth_service: AuthServiceDep, token: AuthTokenDep
) -> dict:
    await auth_service.logout(token)
    request.session.clear()
    return RedirectResponse(url="/")


# @router.post("reset-password")
# async def resert_password_controller():
