from ..repositories import UserRepository
from ..models import User

from sqlalchemy import select


class UserService(UserRepository):
    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.session.execute(select(User).where(User.email == email))
        return user.scalars().first()

    async def get_user_by_github_id(self, github_id: str) -> User | None:
        user = await self.session.execute(
            select(User).where(User.github_id == github_id)
        )
        return user.scalars().first()
