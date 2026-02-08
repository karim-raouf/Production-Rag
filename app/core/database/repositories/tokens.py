from .interfaces import Repository
from ..models import Token
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import TokenCreate, TokenUpdate
from sqlalchemy import select


class TokenRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def list(
        self, 
        skip:int, 
        take:int
    ) -> list[Token]:
        tokens = await self.session.execute(
            select(Token).offset(skip).limit(take)
        )
        return tokens.scalars().all()
        

    async def get(
        self, 
        token_id: int
    ) -> Token | None:
        token = await self.session.execute(
            select(Token).where(Token.id == token_id)
        )
        return token.scalars().first()

    async def create(
        self, 
        token: TokenCreate
    ) -> Token:
        new_token = Token(**token.model_dump())
        self.session.add(new_token)
        await self.session.commit()
        await self.session.refresh(new_token)
        return new_token

    async def update(
        self, 
        token_id: int, 
        updated_token: TokenUpdate
    ) -> Token | None:
        if not (token := self.get(token_id)):
            return None
        
        for key, value in updated_token.model_dump(exclude_unset=True).items():
            setattr(token, key, value)
        
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def delete(
        self, 
        token_id: int
    ) -> None:
        if not (token := self.get(token_id)):
            return None
        await self.session.delete(token)
        await self.session.commit()
