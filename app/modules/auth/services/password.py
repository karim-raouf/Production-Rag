from passlib.context import CryptContext
import asyncio


class PasswordService:
    pwd_context = CryptContext(
        schemes=["bcrypt"]
    )  # not nedded now -, deprecated="auto"

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.pwd_context.verify, password, hashed_password
        )

    async def get_password_hash(self, password: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.pwd_context.hash, password)
