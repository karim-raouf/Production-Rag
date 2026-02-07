from sqlalchemy.ext.asyncio import create_async_engine

from ..config import get_settings

database_url = get_settings().postgres_url

engine = create_async_engine(database_url, echo=True)
