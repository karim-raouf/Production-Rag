from ..repositories import UserRepository
from ..models import User
from sqlalchemy import select
from pydantic import EmailStr

class UserService(UserRepository):
    async def get_user(
        self,
        email: str
    ) -> User | None:
        user = await self.session.execute(
            select(User).where(User.email == email)
        )
        return user.scalars.first()