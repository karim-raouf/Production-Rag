from .interfaces import Repository
from ..models import User
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import UserInDB
from sqlalchemy import select
from pydantic import UUID4
from collections.abc import Sequence


class UserRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int, take: int) -> Sequence[User]:
        query = select(User).offset(skip).limit(take)
        return self.session.scalars(query).all()

    async def get(self, user_id: UUID4) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, user: UserInDB) -> User:
        new_user = User(**user.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def update(self, user_id: UUID4, updated_user: UserInDB) -> User | None:
        if not (user := self.get(user_id)):
            return None
        for key, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID4) -> None:
        user = self.get(user_id)
        self.session.delete(user)
        await self.session.commit()
