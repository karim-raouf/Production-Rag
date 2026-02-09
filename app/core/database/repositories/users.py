from .interfaces import Repository
from ..models import User
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import UserCreate, UserInDB
from sqlalchemy import select
from pydantic import UUID4

class UserRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, 
        skip: int, 
        take: int
    ) -> list[User]:
        users = await self.session.execute(
            select(User).offset(skip).limit(take)
        )
        return users.scalars().all()



    async def get(
        self, 
        user_id: UUID4
    ) -> User | None:
        user = await self.session.execute(select(User).where(User.id == user_id))
        return user.scalars().first()



    async def create(
        self, 
        user: UserInDB
    ) -> User:
        new_user = User(**user.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user



    async def update(
        self, 
        user_id: UUID4, 
        updated_user: UserInDB
    ) -> User | None:
        if not (user := self.get(user_id)):
            return None
        for key, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user



    async def delete(
        self, 
        user_id: UUID4
    ) -> None:
        user = self.get(user_id)
        self.session.delete(user)
        await self.session.commit()
