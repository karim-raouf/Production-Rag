from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Sequence


class Repository(ABC):
    @abstractmethod
    async def get_all(self) -> Sequence[Any]:
        pass

    @abstractmethod
    async def get(self, uid: int) -> Any:
        pass

    @abstractmethod
    async def create(self, record: Any) -> Any:
        pass

    @abstractmethod
    async def update(self, uid: int, record: Any) -> Any:
        pass

    @abstractmethod
    async def delete(self, uid: int) -> None:
        pass
