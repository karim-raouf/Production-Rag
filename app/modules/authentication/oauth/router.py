from .github.router import router as github_router
from fastapi import APIRouter

oauth_router = APIRouter(
    prefix="/oauth",
    tags=["Open Authorization"]
)

oauth_router.include_router(github_router)