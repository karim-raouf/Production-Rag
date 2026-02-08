from datetime import UTC, datetime, timedelta
from ....modules.authentication.exceptions import UnauthorizedException
from jose import JWTError, jwt
from pydantic import UUID4
from ..repositories import TokenRepository
from ..models import Token
from sqlalchemy import select


class TokenService(TokenRepository):
    secret_key = "your_secret_key"
    algorithm = "HS256"
    expires_in_minutes = 60

    