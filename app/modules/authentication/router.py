from typing import Annotated
from ...core.database.models import User
from fastapi import APIRouter, Depends
from ...core.database.schemas import TokenOut, UserOut, UserCreate
from .services import AuthService
from ...core.database.dependencies import DBSessionDep
from .dependencies import AuthHeaderDep, LoginFormDep



router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(session: DBSessionDep):
    return AuthService(session)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@router.post("/register")
async def register_user_controller(
    user: UserCreate,
    auth_service: AuthServiceDep
) -> UserOut:
    return await auth_service.register_user(user)


@router.post("/token")
async def login_for_access_token_controller(
    auth_service: AuthServiceDep,
    form_data: LoginFormDep
) -> TokenOut:
    token = await auth_service.authenticate_user(form_data)
    return {"access_token": token, "token_type": "Bearer"}


@router.post("/logout")
async def logout_access_token_controller(
    auth_service: AuthServiceDep,
    credentials: AuthHeaderDep
) -> dict:
    await auth_service.logout(credentials)
    return {"message": "Logged out"}


# @router.post("reset-password")
# async def resert_password_controller():