from slowapi import Limiter
from starlette.requests import Request
from .database.services import TokenService

def get_user_id_key(request: Request):
    if token := request.session.get("access_token"):
        try:
            
            payload = TokenService().decode(token)
            if user_id := payload.get("sub"):
                return user_id
        except Exception:
            pass

    return request.client.host


limiter = Limiter(key_func=get_user_id_key)