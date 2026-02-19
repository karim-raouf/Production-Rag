from fastapi import Request
from .database.services import TokenService


async def get_user_id(request: Request):
    if token := request.session.get("access_token"):
        try:
            payload = TokenService().decode(token)
            if user_id := payload.get("sub"):
                return user_id
        except Exception:
            pass

    return request.client.host
